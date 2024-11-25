import csv
from netmiko import ConnectHandler

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

def configure_layer3_switch_from_csv(csv_file, switch_ip, vtp_mode, vtp_domain):
    # Connection setup
    print(f"Connecting to Layer 3 switch at {switch_ip}...")
    cat3560 = {
        'device_type': 'cisco_ios',
        'host': switch_ip,
        'username': 'admin',
        'password': 'iloveramsticks',
        'port': 22,
    }
    net_connect = ConnectHandler(**cat3560)
    print("Connection established.")
    
    # Configure VTP mode and domain
    print(f"Configuring VTP mode to '{vtp_mode}' and domain to '{vtp_domain}'...")
    vtp_commands = [
        f"vtp mode {vtp_mode}",
        f"vtp domain {vtp_domain}",
        "vtp password secretpassword"  # Optionally add a VTP password
    ]
    net_connect.send_config_set(vtp_commands)
    
    # Read the CSV file and configure VLANs
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
            switch_num = row["Switch"]
            
            # Parse VLAN range if applicable
            vlan_ids = parse_vlan_range(vlan_str)

            # Command set for configuring VLAN interface and switch ports
            if ip_address and netmask:  # If IP address and netmask are present
                commands = [
                    "conf t",
                    f"vlan {vlan_ids[0]}",  # Assuming the first VLAN for interface configuration
                    f"name {description}",
                    f"interface vlan{vlan_ids[0]}",
                    f"description {description}",
                    f"ip address {ip_address} {netmask}",
                    "no shut"
                ]
                # Send IP configuration for VLAN interface
                net_connect.send_config_set(commands)
                
                # Configure port range for the switch (based on the 'Ports' field)
                port_range = f"FastEthernet 0/{ports}"
                port_commands = [
                    f"interface range {port_range}",
                    f"switchport mode access",
                    f"switchport access vlan {vlan_ids[0]}",
                    "no shut"
                ]
                net_connect.send_config_set(port_commands)
                
            else:  # If no IP address is provided, just configure the ports
                # Check if 'trunk' or 'uplink' is in the Description
                if 'trunk' in description.lower() or 'uplink' in description.lower():
                    # If trunking is needed
                    if vlan_ids:
                        vlan_filtering = ",".join(vlan_ids)
                        commands = [
                            "conf t",
                            f"interface range FastEthernet 0/{ports}",
                            "switchport mode trunk",
                            f"switchport trunk allowed vlan {vlan_filtering}",
                            "no shut"
                        ]
                    else:
                        commands = [
                            "conf t",
                            f"interface range FastEthernet 0/{ports}",
                            "switchport mode trunk",
                            "no shut"
                        ]
                else:
                    commands = [
                        "conf t",
                        f"vlan {vlan_ids[0]}",  # For access port configuration
                        f"name {description}",
                        f"interface range FastEthernet 0/{ports}",
                        f"switchport mode access",
                        f"switchport access vlan {vlan_ids[0]}",
                        "no shut"
                    ]
                
                # Send the commands for trunk or access port
                net_connect.send_config_set(commands)
            
            # Save configuration to memory
            net_connect.send_command("end")
            #net_connect.send_command("wr mem")
            
            print(f"VLAN {vlan_ids[0]} and ports {ports} configured successfully.")

            output = net_connect.send_config_set(commands)
            print(output)
    
    # Closing connection
    print("Configuration complete. Disconnecting...")
    net_connect.disconnect()

if __name__ == "__main__":
    csv_file = "layer3.csv"  # Path to your CSV file
    switch_ip = "192.168.100.100"  # IP address of the Layer 3 switch
    vtp_mode = "transparent"  # Set VTP mode to 'transparent'
    vtp_domain = "howest"  # Set your VTP domain
    configure_layer3_switch_from_csv(csv_file, switch_ip, vtp_mode, vtp_domain)
