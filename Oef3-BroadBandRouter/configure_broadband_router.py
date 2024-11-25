import csv
from netmiko import ConnectHandler

def generate_cisco_config(csv_file, output_file):
    """Generate Cisco configuration from CSV."""
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file, delimiter=';')
        
        # Open the output file where the configuration will be saved (if local)
        with open(output_file, mode='w') as out_file:
            # Write a header to the output file (optional)
            out_file.write("! Cisco Router Configuration\n")
            out_file.write("! Generated from CSV\n\n")
            
            # Loop through each row in the CSV
            for row in csv_reader:
                network_type = row['network'].strip()
                interface = row['interface'].strip()
                description = row['description'].strip()
                vlan = row['vlan'].strip()
                ip_address = row['ipaddress'].strip()
                subnetmask = row['subnetmask'].strip()
                default_gateway = row['defaultgateway'].strip()
                
                # Start with interface configuration
                out_file.write(f"interface {interface}\n")
                out_file.write(f" description {description}\n")
                
                # If IP address is available, configure IP address
                if ip_address and subnetmask:
                    out_file.write(f" ip address {ip_address} {subnetmask}\n")
                if default_gateway:
                    out_file.write(f" ip default-gateway {default_gateway}\n")
                if vlan != "0":  # If it's not the default VLAN (0)
                    out_file.write(f" switchport access vlan {vlan}\n")
                
                # If DHCP is used, configure DHCP
                if ip_address.lower() == "dhcp":
                    out_file.write(f" ip address dhcp\n")
                
                out_file.write(" no shutdown\n\n")  # Bring the interface up
            
            # End of configuration
            out_file.write("! End of Configuration\n")
            print(f"Configuration saved to {output_file}.")

def configure_router_remotely(csv_file, router_ip, username, password):
    """Configure router remotely using Netmiko."""
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file, delimiter=';')
        
        # Setup SSH connection with Netmiko
        device = {
            'device_type': 'cisco_ios',
            'host': router_ip,
            'username': username,
            'password': password,
            'port': 22,
        }
        
        # Connect to the router
        with ConnectHandler(**device) as net_connect:
            print(f"Connected to {router_ip} via SSH.")
            
            # Loop through each row in the CSV and send configuration commands
            for row in csv_reader:
                network_type = row['network'].strip()
                interface = row['interface'].strip()
                description = row['description'].strip()
                vlan = row['vlan'].strip()
                ip_address = row['ipaddress'].strip()
                subnetmask = row['subnetmask'].strip()
                default_gateway = row['defaultgateway'].strip()
                
                # Start with interface configuration
                commands = [
                    f"interface {interface}",
                    f" description {description}",
                ]
                
                # If IP address is available, configure IP address
                if ip_address and subnetmask:
                    commands.append(f" ip address {ip_address} {subnetmask}")
                if default_gateway:
                    commands.append(f" ip default-gateway {default_gateway}")
                if vlan != "0":  # If it's not the default VLAN (0)
                    commands.append(f" switchport access vlan {vlan}")
                
                # If DHCP is used, configure DHCP
                if ip_address.lower() == "dhcp":
                    commands.append(f" ip address dhcp")
                
                commands.append(" no shutdown")
                
                # Send the configuration commands
                net_connect.send_config_set(commands)
                
            # Save the configuration
            net_connect.save_config()
            print("Configuration applied remotely.")

if __name__ == "__main__":
    # Ask the user for the operation mode
    mode = input("Would you like to configure the router remotely (R) or locally (L)? (R/L): ").strip().lower()

    # CSV input and router details
    csv_file = "config4.csv"  # Path to your CSV file
    output_file = "router_config.txt"  # Path to output configuration text file

    if mode == 'l':
        # Local mode - write configuration to a text file
        generate_cisco_config(csv_file, output_file)
    elif mode == 'r':
        # Remote mode - apply configuration via Netmiko
        router_ip = "192.168.100.100"
        username = "adminuser"
        password = "iloveramsticks"
        configure_router_remotely(csv_file, router_ip, username, password)
    else:
        print("Invalid input. Please choose 'R' for remote or 'L' for local.")
