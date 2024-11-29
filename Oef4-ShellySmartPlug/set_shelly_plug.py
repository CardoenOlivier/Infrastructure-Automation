import requests
import json
import argparse

BASE_URL = "http://192.168.33.1"

def set_device_name(device_name):
    url = f"{BASE_URL}/settings"
    payload = {"name": device_name}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"Device name set to {device_name}")
    else:
        print(f"Failed to set device name. Status code: {response.status_code}")

def configure_relay_default_state():
    url = f"{BASE_URL}/relay/0"
    payload = {"default_state": "off"}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Relay default state set to OFF")
    else:
        print(f"Failed to configure relay. Status code: {response.status_code}")

def disable_leds():
    url = f"{BASE_URL}/settings"
    payload = {"led_status_disable": True, "led_power_disable": True}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("LEDs disabled")
    else:
        print(f"Failed to disable LEDs. Status code: {response.status_code}")

def configure_mqtt(broker_ip, subtopic):
    url = f"{BASE_URL}/mqtt"
    payload = {
        "enable": True,
        "server": broker_ip,
        "user": "",
        "id": subtopic,
        "topic_prefix": subtopic
    }
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"MQTT configured with broker {broker_ip} and subtopic {subtopic}")
    else:
        print(f"Failed to configure MQTT. Status code: {response.status_code}")

def disable_unused_services():
    url = f"{BASE_URL}/settings"
    payload = {"cloud_enabled": False}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print("Unused services disabled")
    else:
        print(f"Failed to disable unused services. Status code: {response.status_code}")

def set_max_power(max_power):
    url = f"{BASE_URL}/settings/relay/0"
    payload = {"max_power": max_power}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"Max power set to {max_power}W")
    else:
        print(f"Failed to set max power. Status code: {response.status_code}")

def configure_wifi(ssid, password):
    url = f"{BASE_URL}/wifi"
    payload = {"ssid": ssid, "key": password}
    response = requests.post(url, json=payload)
    if response.status_code == 200:
        print(f"WiFi configured to SSID {ssid}")
    else:
        print(f"Failed to configure WiFi. Status code: {response.status_code}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Configure a Shelly Smart Plug.")
    parser.add_argument("--name", type=str, default="Cardoen-Olivier-Outlet1", help="Device name")
    parser.add_argument("--cloud", action="store_true", help="Enable cloud connection")
    args = parser.parse_args()

    # Device Configuration
    set_device_name(args.name)
    configure_relay_default_state()
    disable_leds()
    configure_mqtt("172.23.83.254", args.name)
    disable_unused_services() if not args.cloud else None
    set_max_power(2200)
    configure_wifi("Howest-IoT", "")
