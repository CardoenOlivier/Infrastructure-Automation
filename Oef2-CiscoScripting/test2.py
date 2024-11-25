import csv

def parse_vlan_range(vlan_range_str):
    """Parse VLAN range (e.g., '300-400') and return a list of VLANs."""
    vlan_list = []
    if '-' in vlan_range_str:
        start_vlan, end_vlan = vlan_range_str.split('-')
        for vlan in range(int(start_vlan), int(end_vlan) + 1):
            vlan_list.append(str(vlan))
    else:
        vlan_list.append(vlan_range_str)  # Single VLAN
    return vlan_list

def generate_layer3_switch_config(csv_file, output_file, vtp_mode, vtp_domain):
    # Open the output file where we will save the configuration
    with open(output_file, 'w') as config_file:
        config_file.write(f"vtp mode {vtp_mode}\n")
        config_file.write(f"vtp domain {vtp_domain}\n")
        config_file.write("vtp password secretpassword\n")  # Optionally add a VTP password
        config_file.write("!\n")  # Separator for clarity

        # Read the CSV file and generate VLAN configuration
        print(f"Reading CSV file: {csv_file}")
        with open(csv_file, mode="r") as file:
            csv_reader = csv.DictReader(file, delimiter=';')
            
            for row_num, row in enumerate(csv_reader, start=1):
                # Clean headers and values (strip spaces)
                row = {key.strip(): value.strip() for key, value in row.items()}
                
                print(f"Processing row {row_num}: VLAN {row['Vlan']} - {row['Description']}")
                
                # Determine VLAN and IP Address configuration
                vlan_str = row["Vlan"]
                description = row["Description"]
                ip_address = row.get("IP Address", "")
                netmask = row.get("Netmask", "")
                ports = row["Ports"]
                
                # Parse VLAN range if applicable
                vlan_ids = parse_vlan_range(vlan_str)

                # Write VLAN interface and port configuration to the output file
                if ip_address and netmask:  # If IP address and netmask are present
                    config_file.write(f"conf t\n")
                    config_file.write(f"vlan {vlan_ids[0]}\n")
                    config_file.write(f"name {description}\n")
                    config_file.write(f"interface vlan{vlan_ids[0]}\n")
                    config_file.write(f"description {description}\n")
                    config_file.write(f"ip address {ip_address} {netmask}\n")
                    config_file.write("no shut\n")
                    config_file.write("!\n")

                    # Configure port range for the switch (based on the 'Ports' field)
                    port_range = f"FastEthernet 0/{ports}"
                    config_file.write(f"interface range {port_range}\n")
                    config_file.write(f"switchport mode access\n")
                    config_file.write(f"switchport access vlan {vlan_ids[0]}\n")
                    config_file.write("no shut\n")
                    config_file.write("!\n")
                else:  # If no IP address is provided, just configure the ports
                    # Check if 'trunk' or 'uplink' is in the Description
                    if 'trunk' in description.lower() or 'uplink' in description.lower():
                        # If trunking is needed
                        if vlan_ids:
                            vlan_filtering = ",".join(vlan_ids)
                            config_file.write(f"conf t\n")
                            config_file.write(f"interface range FastEthernet 0/{ports}\n")
                            config_file.write(f"switchport mode trunk\n")
                            config_file.write(f"switchport trunk allowed vlan {vlan_filtering}\n")
                            config_file.write("no shut\n")
                            config_file.write("!\n")
                        else:
                            config_file.write(f"conf t\n")
                            config_file.write(f"interface range FastEthernet 0/{ports}\n")
                            config_file.write(f"switchport mode trunk\n")
                            config_file.write("no shut\n")
                            config_file.write("!\n")
                    else:
                        config_file.write(f"conf t\n")
                        config_file.write(f"vlan {vlan_ids[0]}\n")
                        config_file.write(f"name {description}\n")
                        config_file.write(f"interface range FastEthernet 0/{ports}\n")
                        config_file.write(f"switchport mode access\n")
                        config_file.write(f"switchport access vlan {vlan_ids[0]}\n")
                        config_file.write("no shut\n")
                        config_file.write("!\n")

        # End of the configuration
        config_file.write("end\n")
        print(f"Configuration written to {output_file}.")

if __name__ == "__main__":
    csv_file = "layer3.csv"  # Path to your CSV file
    output_file = "switch_config.txt"  # Path to the output text file
    vtp_mode = "transparent"  # Set VTP mode to 'transparent'
    vtp_domain = "howest"  # Set your VTP domain
    generate_layer3_switch_config(csv_file, output_file, vtp_mode, vtp_domain)
