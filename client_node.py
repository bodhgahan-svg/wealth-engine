import time
import requests

GATEWAY_URL = "https://your-gateway-url.up.railway.app/api/node/heartbeat"
NODE_ID = "user_unique_device_xyz"

def start_background_node():
    print("🚀 DePIN बैकग्राउंड नोड एक्टिव हो गया है...")
    while True:
        try:
            payload = {
                "node_id": NODE_ID,
                "ip_address": "auto_detected_ip",
                "bytes": 2048 # पास किया गया डेटा साइज
            }
            res = requests.post(GATEWAY_URL, json=payload)
            print(f"💓 हार्टबीट सक्सेसफुल: {res.json()}")
        except Exception as e:
            print(f"⚠️ कनेक्शन एरर: {e}")
        
        # हर 30 सेकंड में सर्वर को सिग्नल भेजना ताकि पता चले नोड जिंदा है
        time.sleep(30)

if __name__ == "__main__":
    start_background_node()
