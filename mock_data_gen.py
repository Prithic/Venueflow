import firebase_admin
from firebase_admin import credentials, db
import random
import time
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def run_simulation():
    """
    Starts the crowd movement simulation engine.
    Pushes randomized queue data to Firebase to simulate live event traffic.
    """
    db_url = os.getenv("FIREBASE_DATABASE_URL")
    cred_path = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "serviceAccountKey.json")

    try:
        if not firebase_admin._apps:
            cred = credentials.Certificate(cred_path)
            firebase_admin.initialize_app(cred, {'databaseURL': db_url})
    except Exception as e:
        print(f"Simulation startup error: {e}")
        return

    print("VenueFlow Simulation Engine Active...")
    while True:
        data = {
            "gate_a": random.randint(2, 45),
            "gate_b": random.randint(2, 45),
            "food_court": random.randint(5, 40),
            "merch_stand": random.randint(1, 15)
        }
        db.reference('queues').set(data)
        print(f"Metrics Synced: {data}")
        time.sleep(5)

if __name__ == "__main__":
    run_simulation()
