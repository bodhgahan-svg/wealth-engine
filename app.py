import os
from fastapi import FastAPI
from fastapi.responses import HTMLResponse

app = FastAPI(title="Autonomous Wealth & Search Engine")

# लाइव वॉलेट लेजर
user_wallets = {
    "global_user": {"balance_inr": 1500.00, "background_mining": "Active"}
}

@app.get("/", response_class=HTMLResponse)
def read_root():
    balance = user_wallets["global_user"]["balance_inr"]
    return f"""
    <!DOCTYPE html>
    <html lang="hi">
    <head>
        <meta charset="UTF-8">
        <title>Invisible Wealth Engine</title>
        <style>
            body {{ font-family: Arial, sans-serif; background: #0f172a; color: #f8fafc; text-align: center; padding: 50px; }}
            .card {{ background: #1e293b; padding: 30px; border-radius: 12px; display: inline-block; box-shadow: 0 4px 20px rgba(0,0,0,0.5); }}
            input {{ padding: 12px; width: 300px; border-radius: 6px; border: none; margin-top: 15px; background: #334155; color: white; }}
            button {{ padding: 12px 20px; background: #22c55e; color: white; border: none; border-radius: 6px; cursor: pointer; font-weight: bold; margin-top: 10px; }}
            .wallet {{ color: #4ade80; font-size: 24px; margin-top: 20px; }}
        </style>
    </head>
    <body>
        <div class="card">
            <h1>🚀 Autonomous AI Search & Wealth Engine</h1>
            <p>बिना विज्ञापन, शुद्ध सर्च और बैकग्राउंड ऑटो-अर्निंग का मॉडल</p>
            <div class="wallet">💰 लाइव वॉलेट बैलेंस: ₹<span id="bal">{balance}</span></div>
            <br>
            <input type="text" id="query" placeholder="यहाँ कुछ भी सर्च करें..."><br>
            <button onclick="triggerSearch()">सर्च करें और कमाई बढ़ाएं</button>
            <p id="result" style="margin-top:20px; color:#94a3b8;"></p>
        </div>
        <script>
            async function triggerSearch() {{
                const q = document.getElementById('query').value;
                if(!q) return;
                const res = await fetch('/api/search?query=' + encodeURIComponent(q));
                const data = await res.json();
                document.getElementById('bal').innerText = data.current_balance;
                document.getElementById('result').innerText = "सर्च रिजल्ट: " + data.result + " | (खाते में ₹" + data.added + " जोड़ दिए गए हैं)";
            }}
        </script>
    </body>
    </html>
    """

@app.get("/api/search")
def search_engine(query: str):
    user_wallets["global_user"]["balance_inr"] += 12.50
    return {
        "query": query,
        "result": f"'{query}' के लिए शुद्ध और सुरक्षित परिणाम (No Ads).",
        "added": 12.50,
        "current_balance": round(user_wallets["global_user"]["balance_inr"], 2)
    }

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run(app, host="0.0.0.0", port=port)
