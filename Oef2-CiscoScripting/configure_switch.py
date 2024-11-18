import csv
from netmiko import ConnectHandler

def configure_vlan_layer2(ssh, vlan_id, description, ports, ip_address=None, netmask=None):
    print(f"Configuring VLAN {vlan_id} with description '{description}'...")

    # Enter enable mode
    ssh.enable()
    print("Entered enable mode.")

    # VLAN configuration
    vlan_commands = [f"vlan {vlan_id}", f"name {description}"]
    if ip_address and netmask:
        vlan_commands.append(f"ip address {ip_address} {netmask}")
        print(f"Configured IP: {ip_address} Netmask: {netmask}")
    else:
        print("No IP address or Netmask provided.")

    print(f"Sending VLAN configuration commands: {vlan_commands}")
    ssh.send_config_set(vlan_commands)

    # Port configuration - directly use the provided port range(s) in Cisco format
    if ports:
        print(f"Configuring ports {ports}...")
        port_commands = [
            f"interface range Fa0/{ports}",
            "switchport mode access",
            f"switchport access vlan {vlan_id}",
            f"description {description}",
        ]
        print(f"Sending port configuration commands: {port_commands}")
        ssh.send_config_set(port_commands)

    # Exit the configuration mode
    print("Exiting configuration mode...")
    ssh.send_command("end")
    print(f"VLAN {vlan_id} configuration completed.")

def configure_switch_from_csv(csv_file, switch_ip):
    # Connection setup
    print(f"Connecting to switch at {switch_ip}...")
    cat3560 = {
        'device_type': 'cisco_ios',
        'host': switch_ip,
        'username': 'admin',
        'password': 'iloveramsticks',
        'port': 22,
    }
    ssh = ConnectHandler(**cat3560)
    print("Connection established.")

    # Reading CSV file and configuring VLANs
    print(f"Reading CSV file: {csv_file}")
    with open(csv_file, mode="r") as file:
        reader = csv.DictReader(file)
        for row in reader:
            vlan = row["Vlan"]
            description = row["Description"]
            ip_address = row["Address"]
            netmask = row["Netmask"]
            ports = row["Ports"]

            print(f"Processing VLAN {vlan}: {description}")
            
            # Ensure that VLAN and description are provided
            if vlan and description:
                configure_vlan_layer2(ssh, vlan, description, ports, ip_address, netmask)

    # Closing connection
    print("Configuration complete. Disconnecting...")
    ssh.disconnect()

if __name__ == "__main__":
    csv_file = "vlans.csv"  # Path to your CSV file
    switch_ip = "192.168.0.10"  # IP address of the switch
    configure_switch_from_csv(csv_file, switch_ip)
 