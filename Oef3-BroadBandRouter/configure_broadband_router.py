import csv
from netmiko import ConnectHandler

def generate_cisco_config(csv_file, output_file):
    """Generate Cisco configuration from CSV."""
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file, delimiter=';')
        
        static_routes = []
        wan_gateway = None

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
                
                # Configure interfaces
                if interface:
                    out_file.write(f"interface {interface}\n")
                    out_file.write(f" description {description}\n")
                    if ip_address.lower() == "dhcp":
                        out_file.write(" ip address dhcp\n")
                    elif ip_address and subnetmask:
                        out_file.write(f" ip address {ip_address} {subnetmask}\n")
                    if vlan != "0":
                        out_file.write(f" switchport access vlan {vlan}\n")
                    out_file.write(" no shutdown\n\n")
                
                # Handle WAN gateway for routing
                if network_type.lower() == "wan" and default_gateway:
                    wan_gateway = default_gateway
                
                # Handle static routes for LAN subnets
                if network_type.lower() == "lan" and default_gateway:
                    static_routes += handle_static_routes(ip_address, subnetmask, default_gateway)

            # Add routing configuration
            out_file.write("! Static Routes Configuration\n")
            if wan_gateway:
                out_file.write(f"ip route 0.0.0.0 0.0.0.0 {wan_gateway}\n")
            for route in static_routes:
                out_file.write(f"{route}\n")
            out_file.write("! IP routing was enabled to allow internet access.\n")
            out_file.write("! End of Configuration\n")
            print(f"Configuration saved to {output_file}.")

def configure_router_remotely(csv_file, router_ip, username, password):
    """Configure router remotely using Netmiko."""
    with open(csv_file, mode='r') as file:
        csv_reader = csv.DictReader(file, delimiter=';')
        
        static_routes = []
        wan_gateway = None

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
            
            for row in csv_reader:
                network_type = row['network'].strip()
                interface = row['interface'].strip()
                description = row['description'].strip()
                vlan = row['vlan'].strip()
                ip_address = row['ipaddress'].strip()
                subnetmask = row['subnetmask'].strip()
                default_gateway = row['defaultgateway'].strip()
                
                commands = []

                # Configure interfaces
                if interface:
                    commands += [
                        f"interface {interface}",
                        f" description {description}",
                    ]
                    if ip_address.lower() == "dhcp":
                        commands.append(" ip address dhcp")
                    elif ip_address and subnetmask:
                        commands.append(f" ip address {ip_address} {subnetmask}")
                    if vlan != "0":
                        commands.append(f" switchport access vlan {vlan}")
                    commands.append(" no shutdown")
                
                # Handle WAN gateway for routing
                if network_type.lower() == "wan" and default_gateway:
                    wan_gateway = default_gateway
                
                # Handle static routes for LAN subnets
                if network_type.lower() == "lan" and default_gateway:
                    static_routes += handle_static_routes(ip_address, subnetmask, default_gateway)
                
                # Send configuration commands
                if commands:
                    net_connect.send_config_set(commands)
            
            # Add routing configuration
            routing_commands = handle_routing(wan_gateway) + static_routes
            net_connect.send_config_set(routing_commands)
            
            # Save the configuration
            net_connect.save_config()
            print("Configuration applied remotely.")

# Function to handle static routes for specific subnets
def handle_static_routes(network, subnet_mask, default_gateway):
    config_commands = []
    if network and subnet_mask and default_gateway:
        config_commands.append(f"ip route {network} {subnet_mask} {default_gateway}")
    return config_commands

# Function to handle WAN routing
def handle_routing(wan_gateway):
    config_commands = []
    if wan_gateway:
        config_commands.append(f"ip route 0.0.0.0 0.0.0.0 {wan_gateway}")
    return config_commands

if __name__ == "__main__":
    mode = input("Would you like to configure the router remotely (R) or locally (L)? (R/L): ").strip().lower()
    csv_file = "config1.csv"
    output_file = "router_config.txt"
    if mode == 'l':
        generate_cisco_config(csv_file, output_file)
    elif mode == 'r':
        router_ip = "192.168.100.100"
        username = "adminuser"
        password = "iloveramsticks"
        configure_router_remotely(csv_file, router_ip, username, password)
    else:
        print("Invalid input. Please choose 'R' for remote or 'L' for local.")
