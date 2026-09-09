import time
import requests

# असली रेलवे यूआरएल के साथ सही फॉर्मेट
GATEWAY_URL = "https://wealth-engine-production-852c.up.railway.app/api/node/heartbeat"
NODE_ID = "node_alpha_01"

def start_background_node():
    print("🚀 DePIN बैकग्राउंड नोड एक्टिव हो गया है...")
    while True:
        try:
            payload = {
                "node_id": NODE_ID,
                "ip_address": "103.25.x.x", # लाइव टेस्ट के लिए आईपी
                "bytes": 2048
            }
            res = requests.post(GATEWAY_URL, json=payload)
            print(f"💓 हार्टबीट सक्सेसफुल: {res.json()}")
        except Exception as e:
            print(f"⚠️ कनेक्शन एरर: {e}")
        
        time.sleep(30)

if __name__ == "__main__":
    start_background_node()
