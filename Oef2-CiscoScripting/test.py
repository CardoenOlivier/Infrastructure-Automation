from netmiko import ConnectHandler

cat3560 = {
    'device_type': 'cisco_ios',
    'host': '192.168.0.10',
    'username': 'admin',
    'password': 'iloveramsticks',
    'port': 22,
    }

ssh = ConnectHandler(**cat3560)
ssh.enable()

result = ssh.send_command('show ip int br')
print(result)