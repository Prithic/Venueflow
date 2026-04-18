import firebase_admin
from firebase_admin import credentials, db
import random
import time
import os

# ==========================================
# FIREBASE CONFIGURATION (ASIAN REGION)
# ==========================================
DATABASE_URL = "https://venueflow-945cc-default-rtdb.asia-southeast1.firebasedatabase.app"

base_path = os.path.dirname(os.path.abspath(__file__))
key_path = os.path.join(base_path, "serviceAccountKey.json")

try:
    cred = credentials.Certificate(key_path)
    firebase_admin.initialize_app(cred, {'databaseURL': DATABASE_URL})
    print(f"Orchestration Engine Live: {DATABASE_URL}")
except Exception as e:
    print(f"CRITICAL ERROR: {e}")
    exit()

def simulate_orchestration():
    print("--- VenueFlow Crowd Orchestration Active ---")
    while True:
        try:
            # 1. Update Queues
            wait_times = {
                "gate_a": random.randint(1, 45),
                "gate_b": random.randint(1, 45),
                "food_court": random.randint(1, 45),
                "merch_stand": random.randint(1, 45)
            }
            db.reference('queues').set(wait_times)
            
            # 2. CROWD ORCHESTRATION LOGIC
            alert_msg = None
            
            # Check for congestion
            if wait_times["gate_a"] > 25:
                if wait_times["gate_b"] <= 25:
                    alert_msg = f"⚠️ Gate A is congested ({wait_times['gate_a']} min wait). Use Gate B ({wait_times['gate_b']} min wait) for immediate entry."
            elif wait_times["gate_b"] > 25:
                if wait_times["gate_a"] <= 25:
                    alert_msg = f"⚠️ Gate B is congested ({wait_times['gate_b']} min wait). Use Gate A ({wait_times['gate_a']} min wait) for faster entry."
            
            # Check other areas
            if not alert_msg and wait_times["food_court"] > 30:
                alert_msg = f"🍔 Food Court is busy ({wait_times['food_court']} min wait). Consider the Merch Stand snacks for a quick bite."

            # Update the current alert node
            if alert_msg:
                db.reference('notifications/current_alert').set(alert_msg)
                print(f"ALERT: {alert_msg}")
            else:
                db.reference('notifications/current_alert').delete()

            print(f"[{time.strftime('%H:%M:%S')}] Queues Updated: A={wait_times['gate_a']}m, B={wait_times['gate_b']}m")
            
        except Exception as e:
            print(f"Simulation Error: {e}")
        time.sleep(5)

if __name__ == "__main__":
    simulate_orchestration()
