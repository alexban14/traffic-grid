import requests
import time
import xml.etree.ElementTree as ET

# Huawei E3372 API endpoints (Standard Hilink)
MODEM_IP = "192.168.8.1"

def get_tokens():
    try:
        res = requests.get(f"http://{MODEM_IP}/api/webserver/SesTokInfo", timeout=5)
        root = ET.fromstring(res.text)
        return root.find('SesInfo').text, root.find('TokInfo').text
    except Exception as e:
        print(f"[GATEWAY] Failed to get tokens: {e}")
        return None, None

def toggle_data(status):
    session, token = get_tokens()
    if not session or not token:
        return False

    headers = {
        "__RequestVerificationToken": token,
        "Cookie": session,
        "Content-Type": "application/x-www-form-urlencoded; charset=UTF-8"
    }
    # 1 = Connect, 0 = Disconnect
    data = f"<?xml version='1.0' encoding='UTF-8'?><request><dataswitch>{status}</dataswitch></request>"
    try:
        res = requests.post(f"http://{MODEM_IP}/api/dialup/mobile-dataswitch", data=data, headers=headers)
        return "OK" in res.text
    except Exception as e:
        print(f"[GATEWAY] Toggle failed: {e}")
        return False

def trigger_rotation():
    print(f"[GATEWAY] Triggering IP rotation on {MODEM_IP}...")
    if toggle_data(0):
        time.sleep(3)
        if toggle_data(1):
            print("[GATEWAY] IP Rotation Successful. New Orange RO IP assigned.")
            return True
    return False

if __name__ == '__main__':
    trigger_rotation()