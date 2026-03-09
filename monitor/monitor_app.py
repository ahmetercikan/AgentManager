from flask import Flask, render_template, jsonify, request
import json
import os
from datetime import datetime
from flask_cors import CORS

app = Flask(__name__, static_folder='static', template_folder='templates')
CORS(app)

# Global status store (in-memory for simplicity, could be Redis/DB)
# Bu yapı, orchestrator'dan gelen son durumu tutar
current_status = {
    "agent": "Idle",
    "task": "Waiting for tasks...",
    "project": "None",
    "step": "0/0",
    "logs": [],
    "last_updated": datetime.now().isoformat()
}

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/status', methods=['GET'])
def get_status():
    """Frontend'in polling yapacağı endpoint"""
    return jsonify(current_status)

@app.route('/api/update_status', methods=['POST'])
def update_status():
    """Orchestrator'ın durum güncelleyeceği endpoint"""
    global current_status
    data = request.json
    
    # Mevcut logları koru ve yenilerini ekle
    new_log = data.get("log")
    if new_log:
        timestamp = datetime.now().strftime("%H:%M:%S")
        log_entry = f"[{timestamp}] {new_log}"
        current_status["logs"].append(log_entry)
        # Son 50 logu tut
        if len(current_status["logs"]) > 50:
            current_status["logs"] = current_status["logs"][-50:]
            
    # Diğer alanları güncelle
    if "agent" in data: current_status["agent"] = data["agent"]
    if "task" in data: current_status["task"] = data["task"]
    if "project" in data: current_status["project"] = data["project"]
    if "step" in data: current_status["step"] = data["step"]
    
    current_status["last_updated"] = datetime.now().isoformat()
    return jsonify({"success": True})

if __name__ == '__main__':
    # 5000 portunda çalışır
    print("🚀 Monitoring Dashboard çalışıyor: http://localhost:5000")
    app.run(debug=True, port=5000)
