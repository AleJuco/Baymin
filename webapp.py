from flask import Flask, request, render_template_string
import json
import os

# --- CONFIGURATION (EDIT THIS) ---
PI_IP = "206.87.128.246"       # <--- YOUR PI'S IP ADDRESS
PI_USER = "baymini"               # <--- YOUR PI USERNAME
PI_PATH = "/home/baymini" # Where it lands on the Pi 

app = Flask(__name__)

# --- THE HTML WEBSITE CODE (Embedded here so you don't need extra files) ---
HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Baymini Health Portal</title>
    <style>
        body { font-family: 'Segoe UI', sans-serif; background-color: #f4f4f9; display: flex; justify-content: center; padding-top: 50px; }
        .container { background: white; padding: 40px; border-radius: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.1); width: 400px; }
        h1 { color: #ff4444; text-align: center; }
        label { font-weight: bold; display: block; margin-top: 15px; }
        input, textarea { width: 100%; padding: 10px; margin-top: 5px; border: 1px solid #ddd; border-radius: 5px; box-sizing: border-box; }
        button { width: 100%; background-color: #ff4444; color: white; padding: 15px; border: none; border-radius: 5px; margin-top: 20px; font-size: 16px; cursor: pointer; }
        button:hover { background-color: #cc0000; }
        .status { margin-top: 20px; text-align: center; color: green; font-weight: bold; }
        .info-box { background-color: #f0f0f0; color: #666; padding: 10px; border-radius: 5px; font-size: 13px; margin-top: 15px; display: flex; align-items: center; }
        .info-box::before { content: 'ℹ'; font-size: 16px; margin-right: 8px; color: #999; }
    </style>
</head>
<body>
    <div class="container">
        <h1>(●—●) <br>Baymini Setup</h1>
        <form method="POST">
            <label>Patient Name</label>
            <input type="text" name="name" placeholder="e.g. Hiro Hamada" required>
            
            <label>Allergies</label>
            <textarea name="allergies" placeholder="e.g. Peanuts, Shellfish"></textarea>
            
            <label>Medical Conditions</label>
            <textarea name="conditions" placeholder="e.g. Asthma, Diabetes"></textarea>
            
            <div class="info-box">Separate multiple items with commas</div>
            
            <button type="submit">Update Baymini</button>
        </form>
        
        {% if status %}
        <div class="status">{{ status }}</div>
        {% endif %}
    </div>
</body>
</html>
"""

@app.route('/', methods=['GET', 'POST'])
def home():
    status_msg = ""
    local_file = "user_data.json"

    if request.method == 'POST':
        # 1. Get data from the webpage
        allergies_raw = request.form.get('allergies', '')
        conditions_raw = request.form.get('conditions', '')

        new_user = {
            "name": request.form.get('name'),
            "allergies": [a.strip() for a in allergies_raw.split(',') if a.strip()],
            "conditions": [c.strip() for c in conditions_raw.split(',') if c.strip()]
        }

        # 2. Read existing data
        if os.path.exists(local_file):
            with open(local_file, 'r') as f:
                try:
                    users = json.load(f)
                    if not isinstance(users, list):
                        users = []  # Reset if the file is not a list
                except json.JSONDecodeError:
                    users = []  # Reset if the file contains invalid JSON
        else:
            users = []  # Initialize if file doesn't exist

        # 3. Append new user data
        users.append(new_user)

        # 4. Save updated data
        with open(local_file, 'w') as f:
            json.dump(users, f, indent=4)

        # 5. Send to Pi using SCP
        print(f"Sending data to {PI_IP}...")

        # The SCP Command
        cmd = f"scp {local_file} {PI_USER}@{PI_IP}:{PI_PATH}"

        # Execute it
        exit_code = os.system(cmd)

        if exit_code == 0:
            status_msg = "✅ Sent to Baymini successfully!"
        else:
            status_msg = "❌ Error sending to Pi. Check Terminal for password prompt."

    return render_template_string(HTML_TEMPLATE, status=status_msg)

if __name__ == '__main__':
    # Runs the website on localhost:5000
    app.run(port=5000, debug=True)