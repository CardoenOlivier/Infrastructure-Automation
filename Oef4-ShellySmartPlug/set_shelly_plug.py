import requests
import time
from pywifi import PyWiFi, const
import argparse

WIFI_SSID = 'telenet-F39B7AD'  # Je thuisnetwerk voor testen
WIFI_PASSWORD = ''  # Wachtwoord

def send_request(url, method='get', data=None):
    """
    Helper function to send HTTP requests.
    """
    try:
        if method.lower() == 'post':
            response = requests.post(url, data=data)
        else:
            response = requests.get(url, params=data)

        print(f"Request URL: {url}")
        print(f"Response status code: {response.status_code}")
        print(f"Response text: {response.text}")

        if response.status_code == 200:
            print("Request successful.")
        else:
            print("Request failed.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")


def configure_led_settings(ip_address, status_led=None, power_led=None):
    """
    Configure LED settings on the Shelly device.
    """
    settings = {
        "led_status_disable": status_led,
        "led_power_disable": power_led,
    }
    for setting, value in settings.items():
        if value is not None:
            url = f"{ip_address}/settings?{setting}={str(value).lower()}"
            send_request(url)


def update_wifi(ip_address, ssid, password):
    """
    Update the Wi-Fi settings of the Shelly device.
    """
    url = f"{ip_address}/settings/sta?enabled=1&ssid={ssid}&key={password}&ipv4_method=dhcp"
    send_request(url, method='post')


def rename_device(ip_address, name):
    """
    Rename the Shelly device.
    """
    url = f"{ip_address}/settings"
    data = {"name": name}
    send_request(url, method='post', data=data)


def set_power_limit(ip_address, max_power):
    """
    Set the maximum power limit for the Shelly device.
    """
    url = f"{ip_address}/settings/?max_power={max_power}"
    send_request(url, method='post')


def set_relay_default(ip_address, relay_id, state):
    """
    Configure the default state of the relay on the Shelly device.
    """
    url = f"{ip_address}/settings/relay/{relay_id}?default_state={state}"
    send_request(url, method='post')


def setup_mqtt(ip_address, broker_ip, topic, enable=True):
    """
    Configure MQTT settings for the Shelly device.
    """
    payload = {
        "mqtt_server": broker_ip if enable else "",
        "mqtt_enable": enable,
        "mqtt_user": "",
        "mqtt_pass": "",
        "mqtt_id": topic if enable else "",
        "mqtt_max_qos": 0,
        "mqtt_retain": False,
    }
    url = f"{ip_address}/settings"
    send_request(url, method='post', data=payload)


def reboot(ip_address):
    """
    Reboot the Shelly device.
    """
    url = f"{ip_address}/settings/reboot"
    send_request(url, method='post')


def scan_shelly_devices():
    """
    Scan for Shelly devices and return their SSIDs.
    """
    wifi = PyWiFi()
    iface = wifi.interfaces()[0]
    iface.scan()
    time.sleep(2)

    shelly_devices = [
        result.ssid
        for result in iface.scan_results()
        if result.ssid.startswith("shellyplug")
    ]
    return shelly_devices


def connect_to_ap(ssid):
    """
    Connect to a Wi-Fi Access Point with the specified SSID.
    """
    wifi = PyWiFi()
    iface = wifi.interfaces()[0]
    iface.disconnect()
    time.sleep(2)
    iface.scan()
    time.sleep(2)
    scan_results = iface.scan_results()

    for result in scan_results:
        if ssid in result.ssid:
            print(f"Attempting to connect to {result.ssid}...")
            profile = iface.add_network_profile(ssid=result.ssid)
            iface.connect(profile)
            time.sleep(5)

            if iface.status() == const.IFACE_CONNECTED:
                print(f"Connected to {result.ssid}")
                return True
            else:
                print(f"Failed to connect to {result.ssid}")
    return False


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configure Shelly smart plug.")
    parser.add_argument("--name", type=str, default="Cardoen-Olivier-Outlet1", help="Name of the Shelly device")
    parser.add_argument("--enable-cloud", action="store_true", help="Enable MQTT cloud connection")
    parser.add_argument("--broker-ip", type=str, default="172.23.83.254", help="IP address of the MQTT broker")

    args = parser.parse_args()

    try:
        shelly_devices = scan_shelly_devices()
        if not shelly_devices:
            print("No Shelly devices found.")
        else:
            print(f"the following Shelly devices has been found: {shelly_devices}")
            for device_ssid in shelly_devices:
                print(f"Attempting to connect to {device_ssid}...")
                if connect_to_ap(device_ssid):
                    SHELLY_IP = "http://192.168.33.1"  # Default IP
                    configure_led_settings(SHELLY_IP, status_led=True, power_led=True)
                    rename_device(SHELLY_IP, args.name)
                    set_power_limit(SHELLY_IP, 2200)
                    set_relay_default(SHELLY_IP, 0, "off")
                    setup_mqtt(SHELLY_IP, args.broker_ip, args.name, enable=args.enable_cloud)
                    reboot(SHELLY_IP)
                    print("Connection will be lost when configuring Wi-Fi...")
                    update_wifi(SHELLY_IP, WIFI_SSID, WIFI_PASSWORD)
                else:
                    print(f"Could not connect to {device_ssid}.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")
