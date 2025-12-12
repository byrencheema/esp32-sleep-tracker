from flask import Flask, request, render_template_string
from datetime import datetime

app = Flask(__name__)

# Store last 100 readings
data_log = []

@app.route("/")
def receive_data():
    temp = request.args.get("temp", "0")
    hum = request.args.get("hum", "0")
    light = request.args.get("light", "0")
    motion = request.args.get("motion", "0")
    score = request.args.get("score", "0")
    
    # Log data with timestamp
    entry = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "temp": temp,
        "hum": hum,
        "light": light,
        "motion": "YES" if motion == "1" else "NO",
        "score": score
    }
    
    data_log.append(entry)
    if len(data_log) > 100:
        data_log.pop(0)
    
    print(f"Received: Temp={temp}°C, Hum={hum}%, Light={light}, Motion={motion}, Score={score}")
    return f"Data received! Score: {score}"

@app.route("/dashboard")
def dashboard():
    # Get latest reading
    latest = data_log[-1] if data_log else {
        "time": "--:--:--",
        "temp": "0",
        "hum": "0",
        "light": "0",
        "motion": "NO",
        "score": "0"
    }
    
    # Create history table
    history_rows = ""
    for entry in reversed(data_log[-20:]):  # Last 20 readings
        history_rows += f"""
        <tr>
            <td>{entry['time']}</td>
            <td>{entry['temp']}°C</td>
            <td>{entry['hum']}%</td>
            <td>{entry['light']}</td>
            <td>{entry['motion']}</td>
            <td><strong>{entry['score']}</strong></td>
        </tr>
        """
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sleep Monitor Dashboard</title>
        <meta http-equiv="refresh" content="2">
        <style>
            body {{
                font-family: Arial, sans-serif;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                padding: 20px;
            }}
            .container {{
                max-width: 1000px;
                margin: 0 auto;
                background: rgba(255,255,255,0.1);
                padding: 30px;
                border-radius: 15px;
                backdrop-filter: blur(10px);
            }}
            h1 {{
                text-align: center;
                font-size: 2.5em;
                margin-bottom: 10px;
            }}
            .score {{
                text-align: center;
                font-size: 5em;
                font-weight: bold;
                margin: 20px 0;
                color: {'#4ade80' if int(latest['score']) >= 70 else '#fbbf24' if int(latest['score']) >= 40 else '#f87171'};
            }}
            .status {{
                text-align: center;
                font-size: 1.5em;
                margin-bottom: 30px;
            }}
            .metrics {{
                display: grid;
                grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
                gap: 20px;
                margin: 30px 0;
            }}
            .metric {{
                background: rgba(255,255,255,0.15);
                padding: 20px;
                border-radius: 10px;
                text-align: center;
            }}
            .metric-value {{
                font-size: 2em;
                font-weight: bold;
                margin: 10px 0;
            }}
            .metric-label {{
                font-size: 0.9em;
                opacity: 0.8;
            }}
            table {{
                width: 100%;
                border-collapse: collapse;
                margin-top: 30px;
                background: rgba(255,255,255,0.1);
                border-radius: 10px;
                overflow: hidden;
            }}
            th, td {{
                padding: 12px;
                text-align: left;
            }}
            th {{
                background: rgba(255,255,255,0.2);
                font-weight: bold;
            }}
            tr:nth-child(even) {{
                background: rgba(255,255,255,0.05);
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>🌙 Sleep Monitor Dashboard</h1>
            
            <div class="score">{latest['score']}</div>
            <div class="status">
                {'✅ Excellent Sleep Conditions' if int(latest['score']) >= 70 else '⚠️ Fair Conditions' if int(latest['score']) >= 40 else '❌ Poor Sleep Environment'}
            </div>
            
            <div class="metrics">
                <div class="metric">
                    <div class="metric-label">🌡️ Temperature</div>
                    <div class="metric-value">{latest['temp']}°C</div>
                </div>
                <div class="metric">
                    <div class="metric-label">💧 Humidity</div>
                    <div class="metric-value">{latest['hum']}%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">💡 Light Level</div>
                    <div class="metric-value">{latest['light']}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">🏃 Motion</div>
                    <div class="metric-value">{latest['motion']}</div>
                </div>
            </div>
            
            <h2>Recent History</h2>
            <table>
                <thead>
                    <tr>
                        <th>Time</th>
                        <th>Temp</th>
                        <th>Humidity</th>
                        <th>Light</th>
                        <th>Motion</th>
                        <th>Score</th>
                    </tr>
                </thead>
                <tbody>
                    {history_rows}
                </tbody>
            </table>
        </div>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
