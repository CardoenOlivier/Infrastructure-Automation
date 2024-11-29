import csv
from netmiko import ConnectHandler

def configure_switch_from_csv(csv_file, switch_ip, vtp_mode, vtp_domain):
    print(f"Connecting to switch at {switch_ip}...")
    cat3560 = {
        'device_type': 'cisco_ios',
        'host': switch_ip,
        'username': 'admin',
        'password': 'admin123',
        'port': 22,
    }
    net_connect = ConnectHandler(**cat3560)
    print("Connection established.")
    
    print(f"Configuring VTP mode to '{vtp_mode}' and domain to '{vtp_domain}'...")
    vtp_commands = [
        f"vtp mode {vtp_mode}",
        f"vtp domain {vtp_domain}",
        "vtp password secretpassword"
    ]
    net_connect.send_config_set(vtp_commands)
    
    print(f"Reading CSV file: {csv_file}")
    with open(csv_file, mode="r") as file:
        csv_reader = csv.DictReader(file, delimiter=';')
        
        for row_num, row in enumerate(csv_reader, start=1):
            row = {key.strip(): value.strip() for key, value in row.items()}
            
            print(f"Processing row {row_num}: VLAN {row['Vlan']} - {row['Description']}")
            
            ip_address = row.get("IP Address", "")
            vlan_id = row["Vlan"]
            description = row["Description"]
            ports = row["Ports"]

            if not ip_address:
                commands = [
                    "conf t",
                    f"vlan {vlan_id}",
                    f"name {description}",
                    f"interface range FastEthernet 0/{ports}",
                    "switchport mode access",
                    f"switchport access vlan {vlan_id}",
                    "no shut",
                    "end",
                    "wr mem"
                ]
            else:
                commands = [
                    "conf t",
                    f"vlan {vlan_id}",
                    f"name {description}",
                    f"interface vlan{vlan_id}",
                    f"desc {description}",
                    f"ip address {ip_address} {row['Netmask']}",
                    "no shut",
                    "end",
                    "wr mem"
                ]
            
            output = net_connect.send_config_set(commands)
            print(output)
    
    print("Configuration complete. Disconnecting...")
    net_connect.disconnect()

if __name__ == "__main__":
    csv_file = "layer2.csv" 
    switch_ip = "192.168.100.100"
    vtp_mode = "transparent" 
    vtp_domain = "howest"
    configure_switch_from_csv(csv_file, switch_ip, vtp_mode, vtp_domain)
