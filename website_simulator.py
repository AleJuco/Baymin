import json
import os
import time

# --- CONFIGURATION (EDIT THESE) ---
PI_IP = "192.168.1.XX"       # <--- REPLACE with your Pi's actual IP
PI_USER = "pi"               # <--- Usually 'pi'
PI_PASSWORD = "raspberry"    # <--- Your Pi's password (if you haven't set up SSH keys)
PI_DESTINATION = "/home/pi/baymax_data.json" # Where it lands on the Pi

def save_and_send(name, allergies, conditions):
    # 1. Create the Local JSON
    data = {
        "name": name,
        "allergies": allergies,
        "conditions": conditions
    }
    
    filename = "user_data.json"
    with open(filename, "w") as f:
        json.dump(data, f, indent=4)
    
    print(f"\n[Website] User {name} saved locally.")

    # 2. Send to Pi using SCP (Secure Copy)
    # This command uses 'sshpass' to handle the password automatically.
    # If you are on Mac, install it first: brew install sshpass
    # If on Windows, you might need to type the password manually or use a key.
    
    print(f"[Network] Beaming data to Baymax ({PI_IP})...")
    
    # Simple SCP command
    cmd = f"scp {filename} {PI_USER}@{PI_IP}:{PI_DESTINATION}"
    
    # Run it
    result = os.system(cmd)
    
    if result == 0:
        print("SUCCESS: Baymax has been updated!")
    else:
        print("ERROR: Could not connect to Pi. Check IP and Wifi.")

# --- THE "WEBSITE" INTERFACE ---
if __name__ == "__main__":
    print("--- BAYMAX WEB PORTAL (SIMULATOR) ---")
    while True:
        print("\nNew User Sign Up:")
        n = input("Name: ")
        a = input("Allergies: ")
        c = input("Conditions: ")
        
        save_and_send(n, a, c)