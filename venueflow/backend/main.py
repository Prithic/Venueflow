from firebase_functions import https_fn, options
from firebase_admin import initialize_app, db
import json

# Initialize Firebase Admin (Native inside Cloud Functions)
# It automatically uses the project credentials when deployed.
# We set the databaseURL for the Asian region specifically.
initialize_app(options={
    'databaseURL': "https://venueflow-945cc-default-rtdb.asia-southeast1.firebasedatabase.app"
})

@https_fn.on_request(
    region="asia-southeast1",
    cors=options.CorsOptions(allow_origins="*", allow_methods=["POST"])
)
def venueflow_api(req: https_fn.Request) -> https_fn.Response:
    """
    Cloud-native rewrite of the VenueFlow Intelligent Concierge.
    This replaces the FastAPI main.py for Firebase Functions deployment.
    """
    if req.method != "POST":
        return https_fn.Response("Method Not Allowed", status=405)

    try:
        data = req.get_json()
        user_msg = data.get("message", "").lower()
    except:
        return https_fn.Response("Invalid JSON", status=400)

    # 1. Fetch live queue data from Realtime Database
    try:
        queues = db.reference('queues').get() or {}
    except:
        queues = {}

    gate_a = queues.get("gate_a", 0)
    gate_b = queues.get("gate_b", 0)
    food = queues.get("food_court", 0)
    merch = queues.get("merch_stand", 0)

    # 2. Intelligent Decision Logic
    reply = "I'm your VenueFlow concierge. How can I help you today?"

    # Fastest Gate
    if "gate" in user_msg and "fast" in user_msg:
        if gate_a < gate_b:
            reply = f"Gate A is currently fastest ({gate_a}m wait) vs Gate B ({gate_b}m)."
        else:
            reply = f"Gate B is moving faster right now ({gate_b}m wait) vs Gate A ({gate_a}m)."

    # Food & Alternatives
    elif any(word in user_msg for word in ["food", "hungry", "eat", "court"]):
        if food > 25:
            reply = f"The Food Court is busy ({food}m). I recommend the Merch Stand snacks instead—it's only a {merch}m wait!"
        else:
            reply = f"The Food Court is in Central Plaza ({food}m wait). Enjoy!"

    # Restrooms
    elif any(word in user_msg for word in ["restroom", "toilet", "washroom"]):
        reply = "Restrooms are located behind the Food Court and near Gates A/B. They are currently clear."

    # Merch
    elif "merch" in user_msg:
        reply = f"The Merch Stand is next to Gate B. Current wait is {merch} minutes."

    # 3. Return Response
    return https_fn.Response(
        json.dumps({"reply": reply}),
        mimetype="application/json"
    )
