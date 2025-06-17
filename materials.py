import cv2
import numpy as np
import subprocess
import time
import threading
import signal
import sys

# === ADB config ===
# adb_device = "127.0.0.1:5555"
adb_device = "127.0.0.1:21503"

# === Image Templates ===
print("Loading templates...")
template_backpack = cv2.imread("images/backpack.jpg")
template_mansion = cv2.imread("images/mansion.jpg")
template_go = cv2.imread("images/go.jpg")
template_obtain = cv2.imread("images/obtain.jpg")
template_menu = cv2.imread("images/menu.jpg")
template_tap_to_close = cv2.imread("images/tap_to_close.jpg")
template_collect = cv2.imread("images/collect.jpg")
template_return_button = cv2.imread("images/return_button.jpg")
template_start_battle = cv2.imread("images/start_battle.jpg")
template_auto_battle_off = cv2.imread("images/auto_battle_off.jpg")
template_auto_indicate = cv2.imread("images/auto_indicate.jpg")
template_tap_to_continue = cv2.imread("images/tap_to_continue.jpg")

template_materials = {
    "wood": {
        "template": cv2.imread("images/wood.jpg"),
        "action": cv2.imread("images/chopping.jpg")
    },
    "stone": {
        "template": cv2.imread("images/stone.jpg"),
        "action": cv2.imread("images/chopping.jpg")
    },
    "crystal": {
        "template": cv2.imread("images/crystal.jpg"),
        "action": cv2.imread("images/collect.jpg")
    },
    "fur": {
        "template": cv2.imread("images/fur.jpg"),
        "action": cv2.imread("images/battle.jpg")
    }
}

main_screen = (860, 400)

print("All templates loaded successfully.")

# === ADB helpers ===
def adb_exec(cmd):
    subprocess.run(f'adb -s {adb_device} {cmd}', shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

def adb_tap(x, y):
    adb_exec(f'shell input tap {x} {y}')

def adb_swipe_hold(x, y, duration_ms):
    adb_exec(f'shell input swipe {x} {y} {x+1} {y+1} {duration_ms}')

def adb_screencap():
    process = subprocess.run(f'adb -s {adb_device} exec-out screencap -p', shell=True, capture_output=True)
    if process.returncode == 0 and process.stdout:
        return cv2.imdecode(np.frombuffer(process.stdout, np.uint8), cv2.IMREAD_COLOR)
    return None

def find_template(source, template, threshold=0.8):
    if source is None or template is None: return None
    result = cv2.matchTemplate(source, template, cv2.TM_CCOEFF_NORMED)
    _, max_val, _, max_loc = cv2.minMaxLoc(result)
    return max_loc if max_val >= threshold else None

def wait_for_template_and_click(template, label, click_location=None):
    print(f"[WAIT] Looking for {label}...")
    start_time = time.time()
    timeout = 10

    while time.time() - start_time < timeout:
        img = adb_screencap()
        if img is None:
            continue

        loc = find_template(img, template)
        if loc:
            click_pos = click_location if click_location else (loc[0] + template.shape[1] // 2, loc[1] + template.shape[0] // 2)
            print(f"[FOUND] {label}. Clicking {click_pos}.")
            adb_tap(*click_pos)
            time.sleep(1)
            return True

        time.sleep(0.5)

    print(f"[NOT FOUND] {label} after {timeout} seconds.")
    return False

def wait_for_template(template, label):
    print(f"[WAIT] Looking for {label}...")
    start_time = time.time()
    timeout = 10

    while time.time() - start_time < timeout:
        img = adb_screencap()
        if img is None:
            continue

        loc = find_template(img, template)
        if loc:
            return True

        time.sleep(0.5)

    print(f"[NOT FOUND] {label} after {timeout} seconds.")
    return False


def action_worker(name, material, action):
    print("[ACTION] Action thread started.")
    while True:
        wait_for_template_and_click(template_menu, "Menu")
        time.sleep(1)
        wait_for_template_and_click(template_backpack, "Backpack")
        time.sleep(1)
        wait_for_template_and_click(template_mansion, "Mansion")
        time.sleep(1)
        wait_for_template_and_click(material, "Selecting Material...")
        time.sleep(1)
        wait_for_template_and_click(template_obtain, "Obtain button")
        time.sleep(1)
        wait_for_template_and_click(template_go, "Go button")
        time.sleep(5)
        img = adb_screencap()
        if find_template(img, template_go):
            print(f"[INFO] Finish collect material {name}")
            wait_for_template_and_click(template_return_button, "Return button")
            time.sleep(1)
            wait_for_template_and_click(template_return_button, "Return button")
            time.sleep(1)
            adb_tap(*main_screen)
            time.sleep(1)
            break
        while True:
            img = adb_screencap()
            if find_template(img, template_backpack):
                time.sleep(1)
            else:
                break
        wait_for_template_and_click(action, "Collect button")
        time.sleep(2)
        if name == 'fur':
            wait_for_template_and_click(template_start_battle, "Start Battle")
            time.sleep(7)
            check_auto_indicate = wait_for_template(template_auto_indicate, "Auto Indicate")
            if not check_auto_indicate:
                wait_for_template_and_click(template_auto_battle_off, "Auto Battle Off")
            time.sleep(7)
            auto_indicate_counter = 0
            print("[ACTION] Wait for battle end...")
            while True:
                img = adb_screencap()
                if find_template(img, template_auto_indicate):
                    auto_indicate_counter = 0
                    time.sleep(1)
                else:
                    auto_indicate_counter += 1
                    if auto_indicate_counter >= 3:
                        break
            time.sleep(3)
            wait_for_template_and_click(template_tap_to_continue, "Tap to Continue")
            time.sleep(3)
            wait_for_template_and_click(template_tap_to_continue, "Tap to Continue")
            time.sleep(3)
        else:
            wait_for_template_and_click(template_tap_to_close, "Close button")
        time.sleep(2)
    print("[ACTION] Action thread stopped.")

def run_macro_attempt():
    for name, data in template_materials.items():
        print(f"Processing {name} material")
        action_worker(name, data["template"], data["action"])

def main():
    print("[INFO] Collecting materials starting...")

    run_macro_attempt()

    print("[INFO] Collecting materials finished.")

def adb_connect_and_test(ip_port: str) -> bool:
    try:
        # First, check if already connected
        result_devices = subprocess.run(
            ['adb', 'devices'],
            capture_output=True,
            text=True,
            timeout=5
        )

        connected_devices = result_devices.stdout.strip().splitlines()[1:]
        for device in connected_devices:
            if device.startswith(ip_port) and "device" in device:
                print(f"Already connected to {ip_port}")
                return True

        # Not connected, try connecting
        result_connect = subprocess.run(
            ['adb', 'connect', ip_port],
            capture_output=True,
            text=True,
            timeout=5
        )
        print(result_connect.stdout.strip())

        # Recheck devices
        result_devices = subprocess.run(
            ['adb', 'devices'],
            capture_output=True,
            text=True,
            timeout=5
        )

        connected_devices = result_devices.stdout.strip().splitlines()[1:]
        for device in connected_devices:
            if device.startswith(ip_port) and "device" in device:
                return True

        return False

    except Exception as e:
        print(f"Error: {e}")
        return False

if __name__ == "__main__":
    if adb_connect_and_test(adb_device):
        print("ADB device connected successfully!")
        main()
    else:
        print("Failed to connect to ADB device.")
