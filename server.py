from flask import Flask, request, render_template_string
from datetime import datetime

app = Flask(__name__)

data_log = []

@app.route("/")
def receive_data():
    temp = request.args.get("temp", "0")
    hum = request.args.get("hum", "0")
    light = request.args.get("light", "0")
    motion = request.args.get("motion", "0")
    score = request.args.get("score", "0")
    
    entry = {
        "time": datetime.now().strftime("%H:%M:%S"),
        "temp": float(temp),
        "hum": float(hum),
        "light": int(light),
        "motion": "YES" if motion == "1" else "NO",
        "score": int(score)
    }
    
    data_log.append(entry)
    if len(data_log) > 100:
        data_log.pop(0)
    
    print(f"Received: Temp={temp}°C, Hum={hum}%, Light={light}, Motion={motion}, Score={score}")
    return f"Data received! Score: {score}"

@app.route("/dashboard")
def dashboard():
    latest = data_log[-1] if data_log else {
        "time": "--:--:--",
        "temp": 0,
        "hum": 0,
        "light": 0,
        "motion": "NO",
        "score": 0
    }
    
    recent_data = data_log[-50:] if len(data_log) > 0 else []
    
    times = [d["time"] for d in recent_data]
    temps = [d["temp"] for d in recent_data]
    hums = [d["hum"] for d in recent_data]
    lights = [d["light"] for d in recent_data]
    scores = [d["score"] for d in recent_data]
    
    html = f"""
    <!DOCTYPE html>
    <html>
    <head>
        <title>Sleep Monitor</title>
        <meta http-equiv="refresh" content="5">
        <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
        <style>
            * {{
                margin: 0;
                padding: 0;
                box-sizing: border-box;
            }}
            body {{
                font-family: 'Arial', sans-serif;
                background: #000;
                color: #fff;
                padding: 40px 20px;
            }}
            .container {{
                max-width: 1400px;
                margin: 0 auto;
            }}
            h1 {{
                font-size: 2em;
                margin-bottom: 40px;
                font-weight: 300;
                letter-spacing: 2px;
                text-transform: uppercase;
            }}
            .score-box {{
                background: #fff;
                color: #000;
                padding: 60px;
                margin-bottom: 40px;
                border: 2px solid #000;
            }}
            .score {{
                font-size: 8em;
                font-weight: 700;
                line-height: 1;
            }}
            .status {{
                font-size: 1.2em;
                margin-top: 20px;
                font-weight: 300;
                letter-spacing: 1px;
            }}
            .metrics {{
                display: grid;
                grid-template-columns: repeat(4, 1fr);
                gap: 20px;
                margin-bottom: 40px;
            }}
            .metric {{
                background: #fff;
                color: #000;
                padding: 30px;
                border: 2px solid #000;
            }}
            .metric-label {{
                font-size: 0.8em;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 15px;
                opacity: 0.6;
            }}
            .metric-value {{
                font-size: 2.5em;
                font-weight: 700;
            }}
            .charts {{
                display: grid;
                grid-template-columns: repeat(2, 1fr);
                gap: 20px;
            }}
            .chart-box {{
                background: #fff;
                padding: 30px;
                border: 2px solid #000;
            }}
            .chart-title {{
                font-size: 0.9em;
                text-transform: uppercase;
                letter-spacing: 1px;
                margin-bottom: 20px;
                color: #000;
                font-weight: 600;
            }}
            canvas {{
                max-height: 250px;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>Sleep Monitor</h1>
            
            <div class="score-box">
                <div class="score">{latest['score']}</div>
                <div class="status">
                    {'EXCELLENT' if latest['score'] >= 70 else 'FAIR' if latest['score'] >= 40 else 'POOR'}
                </div>
            </div>
            
            <div class="metrics">
                <div class="metric">
                    <div class="metric-label">Temperature</div>
                    <div class="metric-value">{latest['temp']:.1f}°C</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Humidity</div>
                    <div class="metric-value">{latest['hum']:.1f}%</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Light</div>
                    <div class="metric-value">{latest['light']}</div>
                </div>
                <div class="metric">
                    <div class="metric-label">Motion</div>
                    <div class="metric-value">{latest['motion']}</div>
                </div>
            </div>
            
            <div class="charts">
                <div class="chart-box">
                    <div class="chart-title">Comfort Score</div>
                    <canvas id="scoreChart"></canvas>
                </div>
                
                <div class="chart-box">
                    <div class="chart-title">Temperature</div>
                    <canvas id="tempChart"></canvas>
                </div>
                
                <div class="chart-box">
                    <div class="chart-title">Humidity</div>
                    <canvas id="humChart"></canvas>
                </div>
                
                <div class="chart-box">
                    <div class="chart-title">Light Level</div>
                    <canvas id="lightChart"></canvas>
                </div>
            </div>
        </div>
        
        <script>
            const chartOptions = {{
                responsive: true,
                maintainAspectRatio: true,
                plugins: {{
                    legend: {{ display: false }}
                }},
                scales: {{
                    x: {{
                        grid: {{ color: '#e0e0e0' }},
                        ticks: {{ 
                            color: '#000',
                            maxTicksLimit: 8,
                            font: {{ size: 10 }}
                        }}
                    }},
                    y: {{
                        grid: {{ color: '#e0e0e0' }},
                        ticks: {{ 
                            color: '#000',
                            font: {{ size: 10 }}
                        }}
                    }}
                }}
            }};
            
            new Chart(document.getElementById('scoreChart'), {{
                type: 'line',
                data: {{
                    labels: {times},
                    datasets: [{{
                        data: {scores},
                        borderColor: '#000',
                        backgroundColor: 'rgba(0, 0, 0, 0.05)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.1,
                        pointRadius: 0
                    }}]
                }},
                options: chartOptions
            }});
            
            new Chart(document.getElementById('tempChart'), {{
                type: 'line',
                data: {{
                    labels: {times},
                    datasets: [{{
                        data: {temps},
                        borderColor: '#000',
                        backgroundColor: 'rgba(0, 0, 0, 0.05)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.1,
                        pointRadius: 0
                    }}]
                }},
                options: chartOptions
            }});
            
            new Chart(document.getElementById('humChart'), {{
                type: 'line',
                data: {{
                    labels: {times},
                    datasets: [{{
                        data: {hums},
                        borderColor: '#000',
                        backgroundColor: 'rgba(0, 0, 0, 0.05)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.1,
                        pointRadius: 0
                    }}]
                }},
                options: chartOptions
            }});
            
            new Chart(document.getElementById('lightChart'), {{
                type: 'line',
                data: {{
                    labels: {times},
                    datasets: [{{
                        data: {lights},
                        borderColor: '#000',
                        backgroundColor: 'rgba(0, 0, 0, 0.05)',
                        borderWidth: 2,
                        fill: true,
                        tension: 0.1,
                        pointRadius: 0
                    }}]
                }},
                options: chartOptions
            }});
        </script>
    </body>
    </html>
    """
    return render_template_string(html)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
