import firebase_admin
from firebase_admin import credentials, db
import random
import time
import os
from dotenv import load_dotenv

# Load environment variables for security
load_dotenv()

def initialize_orchestration():
    """
    Initializes the Firebase Admin SDK using environment variables.
    Ensures secure credential management and cross-region compatibility.
    """
    database_url = os.getenv("FIREBASE_DATABASE_URL")
    service_account = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")

    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(service_account)
            firebase_admin.initialize_app(cred, {'databaseURL': database_url})
            print(f"Orchestration Engine Live: {database_url}")
    except Exception as e:
        print(f"CRITICAL ERROR: {e}")
        exit()

def simulate_orchestration():
    """
    Main simulation loop for stadium crowd orchestration.
    Generates mock sensor data and pushes real-time routing alerts to Firebase.
    """
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
    initialize_orchestration()
    simulate_orchestration()
