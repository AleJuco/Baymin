from flask import Flask, request, render_template_string, session, redirect, url_for
import json
import os
from datetime import timedelta

# --- CONFIGURATION (EDIT THIS) ---
PI_IP = "206.87.128.246"
PI_USER = "baymini"
PI_PATH = "/home/baymini"

app = Flask(__name__)
app.secret_key = 'baymini-secure-key'
app.permanent_session_lifetime = timedelta(hours=24)

# --- MODERN UI DESIGN SYSTEM ---
BASE_CSS = """
<style>
    @import url('https://fonts.googleapis.com/css2?family=Plus+Jakarta+Sans:wght@400;500;600;700;800&display=swap');

    :root {
        --primary: #FF5A5F;       /* Baymax Red */
        --primary-hover: #E0484D;
        --bg: #F8FAFC;
        --surface: #FFFFFF;
        --text-main: #1E293B;
        --text-sub: #64748B;
        --border: #E2E8F0;
        --success-bg: #DCFCE7;
        --success-text: #166534;
        --error-bg: #FEE2E2;
        --error-text: #991B1B;
        --shadow-sm: 0 1px 2px 0 rgb(0 0 0 / 0.05);
        --shadow-lg: 0 10px 15px -3px rgb(0 0 0 / 0.1), 0 4px 6px -4px rgb(0 0 0 / 0.1);
    }

    * { margin: 0; padding: 0; box-sizing: border-box; }

    body { 
        font-family: 'Plus Jakarta Sans', sans-serif; 
        background-color: var(--bg);
        background-image: radial-gradient(#E2E8F0 1px, transparent 1px);
        background-size: 24px 24px;
        color: var(--text-main);
        line-height: 1.6;
        min-height: 100vh;
        display: flex;
        flex-direction: column;
    }

    /* --- Animations --- */
    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    @keyframes blink {
        0%, 90%, 100% { transform: scaleY(1); }
        95% { transform: scaleY(0.1); }
    }

    .fade-in { animation: fadeIn 0.4s ease-out forwards; }
    
    .baymax-eyes {
        display: inline-block;
        font-weight: 800;
        letter-spacing: -1px;
        color: var(--primary);
        animation: blink 4s infinite;
        transform-origin: center;
    }

    /* --- Navigation --- */
    nav {
        background: rgba(255, 255, 255, 0.9);
        backdrop-filter: blur(12px);
        border-bottom: 1px solid var(--border);
        position: sticky;
        top: 0;
        z-index: 50;
    }

    .nav-container {
        max-width: 1000px;
        margin: 0 auto;
        padding: 1rem 1.5rem;
        display: flex;
        justify-content: space-between;
        align-items: center;
    }

    .logo {
        font-weight: 800;
        font-size: 1.25rem;
        color: var(--text-main);
        text-decoration: none;
        display: flex;
        align-items: center;
        gap: 10px;
    }

    .nav-links a {
        color: var(--text-sub);
        text-decoration: none;
        font-weight: 600;
        font-size: 0.9rem;
        margin-left: 24px;
        transition: all 0.2s;
    }

    .nav-links a:hover { color: var(--primary); }
    .nav-links a.btn {
        background: var(--text-main);
        color: white;
        padding: 8px 20px;
        border-radius: 99px;
    }
    .nav-links a.btn:hover { background: #000; transform: translateY(-1px); }

    /* --- Layout --- */
    .container {
        max-width: 900px;
        margin: 0 auto;
        padding: 2rem 1.5rem;
        flex: 1;
        width: 100%;
    }

    /* --- Cards --- */
    .card {
        background: var(--surface);
        border-radius: 20px;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-lg);
        padding: 2.5rem;
        margin-bottom: 2rem;
        position: relative;
        overflow: hidden;
    }

    .card::before {
        content: "";
        position: absolute;
        top: 0; left: 0; right: 0; height: 4px;
        background: linear-gradient(90deg, var(--primary), #FF8F93);
    }

    /* --- Typography --- */
    h1 { font-size: 2.2rem; font-weight: 800; letter-spacing: -0.03em; margin-bottom: 1rem; color: var(--text-main); }
    h2 { font-size: 1.5rem; font-weight: 700; margin-bottom: 1.5rem; color: var(--text-main); }
    p { color: var(--text-sub); margin-bottom: 1.5rem; }

    /* --- Forms --- */
    label {
        display: block;
        font-weight: 600;
        font-size: 0.85rem;
        text-transform: uppercase;
        letter-spacing: 0.05em;
        color: var(--text-sub);
        margin-bottom: 8px;
        margin-top: 20px;
    }

    input, textarea {
        width: 100%;
        padding: 14px 16px;
        border: 2px solid var(--border);
        border-radius: 12px;
        font-size: 1rem;
        background: #F8FAFC;
        font-family: inherit;
        transition: all 0.2s;
    }

    input:focus, textarea:focus {
        outline: none;
        background: white;
        border-color: var(--primary);
        box-shadow: 0 0 0 4px rgba(255, 90, 95, 0.1);
    }

    textarea { resize: vertical; min-height: 100px; }

    /* --- Buttons --- */
    button {
        width: 100%;
        background: var(--primary);
        color: white;
        border: none;
        padding: 16px;
        font-size: 1rem;
        font-weight: 700;
        border-radius: 12px;
        cursor: pointer;
        transition: all 0.2s;
        margin-top: 10px;
        box-shadow: 0 4px 6px -1px rgba(255, 90, 95, 0.3);
    }

    button:hover { 
        background: var(--primary-hover); 
        transform: translateY(-2px); 
        box-shadow: 0 10px 15px -3px rgba(255, 90, 95, 0.4);
    }

    button.secondary {
        background: transparent;
        color: var(--text-sub);
        box-shadow: none;
        border: 2px solid var(--border);
    }

    button.secondary:hover { background: white; color: var(--text-main); border-color: var(--text-main); }

    /* --- Alerts --- */
    .alert {
        padding: 16px;
        border-radius: 12px;
        margin-bottom: 24px;
        font-weight: 600;
        display: flex;
        align-items: center;
        gap: 10px;
    }
    .alert.success { background: var(--success-bg); color: var(--success-text); }
    .alert.error { background: var(--error-bg); color: var(--error-text); }

    /* --- Dashboard Widgets --- */
    .widget-grid {
        display: grid;
        grid-template-columns: repeat(auto-fit, minmax(240px, 1fr));
        gap: 20px;
        margin-bottom: 30px;
    }

    .widget {
        background: white;
        padding: 20px;
        border-radius: 16px;
        border: 1px solid var(--border);
        box-shadow: var(--shadow-sm);
    }

    .widget h3 { font-size: 0.9rem; color: var(--text-sub); text-transform: uppercase; margin-bottom: 5px; }
    .widget .value { font-size: 1.8rem; font-weight: 800; color: var(--text-main); }
    
</style>
"""

def create_page(content, active_page='home'):
    user = session.get('user')
    nav_links = ""
    
    if user:
        nav_links = f"""
            <a href="/dashboard">Dashboard</a>
            <a href="/logout" class="btn">Sign Out</a>
        """
    else:
        nav_links = f"""
            <a href="/login">Log In</a>
            <a href="/signup" class="btn">Get Started</a>
        """

    return f"""
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Baymini | AI Health</title>
        {BASE_CSS}
    </head>
    <body>
        <nav>
            <div class="nav-container">
                <a href="/" class="logo">
                    <span class="baymax-eyes">(●—●)</span> Baymini
                </a>
                <div class="nav-links">
                    {nav_links}
                </div>
            </div>
        </nav>
        
        <div class="container fade-in">
            {content}
        </div>
        
        <footer style="text-align:center; padding: 2rem; color: #94A3B8; font-size: 0.9rem;">
            &copy; 2026 Baymini Health Project • nwHacks
        </footer>
    </body>
    </html>
    """

# --- BACKEND LOGIC ---
def load_users():
    if os.path.exists('users.json'):
        with open('users.json', 'r') as f:
            try: return json.load(f)
            except: return []
    return []

def save_users(users):
    with open('users.json', 'w') as f:
        json.dump(users, f, indent=4)
def save_current_user(user):
    """Save the currently logged-in user to current_user.json for AllergyCheck."""
    current_user_data = {
        "name": user.get('name', 'User'),
        "email": user.get('email', ''),
        "allergies": user.get('allergies', []),
        "conditions": user.get('conditions', []),
        "medications": user.get('medications', [])
    }
    with open('current_user.json', 'w') as f:
        json.dump(current_user_data, f, indent=2)
def sync_to_pi():
    # SIMULATION MODE FOR WINDOWS (To avoid password hanging)
    # If you want real sync, uncomment the os.system line
    print(" [Simulating] Syncing data to Raspberry Pi...")
    
    # Real Command (Uncomment if SSH keys are set up):
    cmd = f"scp -o ConnectTimeout=2 users.json {PI_USER}@{PI_IP}:{PI_PATH}/users.json"
    return os.system(cmd) == 0

# --- ROUTES ---

@app.route('/')
def index():
    user = session.get('user')
    
    if user:
        # LOGGED IN HOME
        content = f"""
        <div class="card" style="text-align: center; padding: 4rem 2rem;">
            <div style="font-size: 5rem; color: var(--primary); margin-bottom: 1rem;" class="baymax-eyes">(●—●)</div>
            <h1>Good Morning, {user['name'].split()[0]}.</h1>
            <p style="font-size: 1.2rem; max-width: 600px; margin: 0 auto 30px auto;">
                I am Baymin, your personal miniature healthcare companion.
            </p>
            
            <a href="/dashboard">
                <button style="width: auto; padding: 18px 48px; font-size: 1.1rem;">
                    Go to Dashboard
                </button>
            </a>
            
            <div style="margin-top: 40px; display: flex; gap: 20px; justify-content: center; opacity: 0.7;">
                <div style="background: #DEF7EC; color: #046C4E; padding: 8px 16px; border-radius: 99px; font-weight: 600; font-size: 0.9rem;">
                    ● System Online
                </div>
                <div style="background: #E0F2FE; color: #0369A1; padding: 8px 16px; border-radius: 99px; font-weight: 600; font-size: 0.9rem;">
                    ● Vision Ready
                </div>
            </div>
        </div>
        """
    else:
        # GUEST HOME
        content = """
        <div style="text-align: center; margin-top: 40px;">
            <div class="baymax-eyes" style="font-size: 4rem; margin-bottom: 20px;">(●—●)</div>
            <h1 style="font-size: 3.5rem; line-height: 1.1; margin-bottom: 20px; background: linear-gradient(135deg, #1E293B 0%, #475569 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent;">
                Your Personal <br>Health Guardian.
            </h1>
            <p style="font-size: 1.25rem; max-width: 600px; margin: 0 auto 40px auto;">
                Baymini uses AI vision to scan food, detect allergens, and keep you safe.
            </p>
            
            <div style="display: flex; gap: 15px; justify-content: center;">
                <a href="/signup"><button style="width: auto; padding: 16px 40px;">Get Started</button></a>
                <a href="/login"><button class="secondary" style="width: auto; padding: 16px 40px;">Log In</button></a>
            </div>
            
            <div class="widget-grid" style="margin-top: 80px; text-align: left;">
                <div class="widget">
                    <div style="font-size: 2rem; margin-bottom: 10px;">👁️</div>
                    <h3 style="color: var(--text-main);">Vision AI</h3>
                    <p style="font-size: 0.9rem;">Instantly recognizes products and reads ingredient labels.</p>
                </div>
                <div class="widget">
                    <div style="font-size: 2rem; margin-bottom: 10px;">🥜</div>
                    <h3 style="color: var(--text-main);">Allergy Alert</h3>
                    <p style="font-size: 0.9rem;">Checks against your personal profile in milliseconds.</p>
                </div>
                <div class="widget">
                    <div style="font-size: 2rem; margin-bottom: 10px;">🗣️</div>
                    <h3 style="color: var(--text-main);">Voice Interface</h3>
                    <p style="font-size: 0.9rem;">Speaks to you naturally just like Baymax.</p>
                </div>
            </div>
        </div>
        """
    return create_page(content)

@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        users = load_users()
        email = request.form.get('email')
        
        if any(u['email'] == email for u in users):
            return create_page(f'<div class="alert error">❌ Email already in use.</div>')
            
        new_user = {
            "name": request.form.get('name'),
            "email": email,
            "password": request.form.get('password'), 
            "allergies": [x.strip() for x in request.form.get('allergies', '').split(',') if x.strip()],
            "conditions": [x.strip() for x in request.form.get('conditions', '').split(',') if x.strip()],
            "medications": [x.strip() for x in request.form.get('medications', '').split(',') if x.strip()]
        }
        users.append(new_user)
        save_users(users)
        
        session.permanent = True
        session['user'] = new_user
        
        sync_to_pi() # Background sync
        return redirect(url_for('welcome'))

    content = """
    <div class="card" style="max-width: 500px; margin: 0 auto;">
        <h2 style="text-align: center;">Create Profile</h2>
        <form method="POST">
            <label>Full Name</label>
            <input type="text" name="name" placeholder="Hiro Hamada" required>
            
            <label>Email Address</label>
            <input type="email" name="email" required>
            
            <label>Password</label>
            <input type="password" name="password" required>
            
            <div style="margin: 30px 0; border-top: 1px solid var(--border);"></div>
            
            <label>Allergies</label>
            <input type="text" name="allergies" placeholder="Peanuts, Shellfish...">
            
            <label>Medical Conditions</label>
            <input type="text" name="conditions" placeholder="Asthma, Diabetes...">
            
            <label>Current Medications</label>
            <input type="text" name="medications" placeholder="Insulin...">
            
            <button type="submit">Complete Setup</button>
        </form>
    </div>
    """
    return create_page(content)

@app.route('/welcome')
def welcome():
    if 'user' not in session: return redirect(url_for('login'))
    
    content = """
    <div class="card" style="max-width: 500px; margin: 40px auto; text-align: center;">
        <div style="width: 80px; height: 80px; background: #DCFCE7; color: #166534; font-size: 40px; border-radius: 50%; display: flex; align-items: center; justify-content: center; margin: 0 auto 20px auto;">✓</div>
        <h1>You are satisfied with your care.</h1>
        <p>Your profile has been created and synced to the Baymini Unit.</p>
        
        <a href="/dashboard"><button>Go to Dashboard</button></a>
    </div>
    """
    return create_page(content)

@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        users = load_users()
        user = next((u for u in users if u['email'] == request.form.get('email') and u['password'] == request.form.get('password')), None)
        if user:
            session['user'] = user
            # Save current user for AllergyCheck
            save_current_user(user)
            return redirect(url_for('dashboard'))
        error = '<div class="alert error">Invalid credentials</div>'

    content = f"""
    <div class="card" style="max-width: 400px; margin: 40px auto;">
        <h2 style="text-align: center;">Welcome Back</h2>
        {error}
        <form method="POST">
            <label>Email</label>
            <input type="email" name="email" required>
            <label>Password</label>
            <input type="password" name="password" required>
            <button type="submit">Log In</button>
        </form>
    </div>
    """
    return create_page(content)

@app.route('/dashboard', methods=['GET', 'POST'])
def dashboard():
    if 'user' not in session: return redirect(url_for('login'))
    user = session['user']
    msg = ""

    # --- STATUS LOGIC ---
    # Change this to False if you want to test the "Red/Offline" look
    device_online = True 
    
    if device_online:
        status_text = "Active"
        status_color = "#166534" # Green
    else:
        status_text = "Offline"
        status_color = "#DC2626" # Red
    # --------------------

    if request.method == 'POST':
        users = load_users()
        for i, u in enumerate(users):
            if u['email'] == user['email']:
                users[i]['allergies'] = [x.strip() for x in request.form.get('allergies', '').split(',') if x.strip()]
                users[i]['conditions'] = [x.strip() for x in request.form.get('conditions', '').split(',') if x.strip()]
                users[i]['medications'] = [x.strip() for x in request.form.get('medications', '').split(',') if x.strip()]
                save_users(users)
                session['user'] = users[i]
                user = users[i]
                # Update current user file for AllergyCheck
                save_current_user(users[i])
                
                if sync_to_pi():
                    msg = '<div class="alert success">✅ Synced to Baymini</div>'
                else:
                    msg = '<div class="alert error">⚠️ Saved, but device offline</div>'
                break

    # Calculate counts for widgets
    allergy_count = len(user.get('allergies', []))
    med_count = len(user.get('medications', []))

    content = f"""
    <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 20px;">
        <h2>Health Dashboard</h2>
        <div style="display: flex; align-items: center; gap: 8px; font-size: 0.9rem; color: {status_color}; background: {'#DCFCE7' if device_online else '#FEE2E2'}; padding: 6px 12px; border-radius: 99px; font-weight: 600;">
            <div style="width: 8px; height: 8px; background: {status_color}; border-radius: 50%;"></div>
            {status_text}
        </div>
    </div>

    {msg}

    <div class="widget-grid">
        <div class="widget">
            <h3>Active Allergies</h3>
            <div class="value">{allergy_count}</div>
        </div>
        <div class="widget">
            <h3>Medications</h3>
            <div class="value">{med_count}</div>
        </div>
        <div class="widget">
            <h3>Baymini Status</h3>
            <div class="value" style="color: {status_color};">{status_text}</div>
        </div>
    </div>

    <div class="card">
        <h2>Edit Profile</h2>
        <form method="POST">
            <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 20px;">
                <div>
                    <label>Allergies</label>
                    <textarea name="allergies">{', '.join(user.get('allergies', []))}</textarea>
                </div>
                <div>
                    <label>Medical Conditions</label>
                    <textarea name="conditions">{', '.join(user.get('conditions', []))}</textarea>
                </div>
            </div>
            
            <label>Current Medications</label>
            <input type="text" name="medications" value="{', '.join(user.get('medications', []))}">
            
            <div style="display: flex; justify-content: flex-end;">
                <button type="submit" style="width: auto; padding-left: 40px; padding-right: 40px;">Save Changes</button>
            </div>
        </form>
    </div>
    """
    return create_page(content, 'dashboard')

@app.route('/logout')
def logout():
    session.pop('user', None)
    return redirect(url_for('index'))

if __name__ == '__main__':
    app.run(port=5001, debug=True)