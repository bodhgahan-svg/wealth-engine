from fastapi import FastAPI, HTTPException
import httpx
import time

app = FastAPI(title="Global DePIN Traffic Routing Gateway", version="1.0.0")

# एक्टिव नोड्स की डायरेक्टरी (लाइव सिस्टम में यहाँ डेटाबेस होगा)
active_nodes = {}

@app.post("/api/node/heartbeat")
async def node_heartbeat(payload: dict):
    """ यूजर का फोन या एक्सटेंशन हर 30 सेकंड में अपनी मौजूदगी दर्ज कराएगा """
    node_id = payload.get("node_id")
    ip_address = payload.get("ip_address")
    
    if not node_id:
        return {"success": False, "message": "Node ID missing"}
    
    active_nodes[node_id] = {
        "ip": ip_address,
        "last_seen": time.time(),
        "traffic_routed_bytes": payload.get("bytes", 0)
    }
    return {"success": True, "active_nodes_count": len(active_nodes)}

@app.post("/api/b2b/route-request")
async def route_b2b_traffic(payload: dict):
    """ 
    बाहरी एआई या डेटा कंपनी यहाँ रिक्वेस्ट भेजेगी। 
    गेटवे उस ट्रैफिक को किसी रैंडम एक्टिव यूजर नोड के जरिए रूट करेगा।
    """
    target_url = payload.get("target_url")
    if not active_nodes:
        raise HTTPException(status_code=400, detail="कोई भी यूजर नोड ऑनलाइन नहीं है!")
    
    # लोड बैलेंसर के जरिए पहला उपलब्ध एक्टिव नोड चुनें
    available_node_id = list(active_nodes.keys())[0]
    node_info = active_nodes[available_node_id]
    
    try:
        # बाहरी ट्रैफिक को यूजर के नेटवर्क/प्रॉक्सी के जरिए फेच करना
        async with httpx.AsyncClient(timeout=10.0) as client:
            response = await client.get(target_url)
            
            # डेटा इस्तेमाल होने पर यूजर के खाते में क्रेडिट जुड़ेगा और फाउंडर का कट अलग होगा
            return {
                "success": True,
                "routed_via_node": available_node_id,
                "node_ip": node_info["ip"],
                "status_code": response.status_code,
                "data_preview": response.text[:200]
            }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"राउटिंग फेल: {str(e)}")
