# VenueFlow 🏟️ | Stadium Coordination & Intelligence System

**VenueFlow** is a high-end, real-time stadium management dashboard designed to solve crowd congestion and improve the attendee experience at large-scale sporting events. Built for speed, intelligence, and visual excellence.

---

## 🚀 Key Features

### 1. **Dynamic Real-Time Dashboard**
- **Live Queue Monitoring:** Track wait times across Gate A, Gate B, Food Courts, and Merch Stands.
- **Visual Intelligence:** Color-coded status indicators (Green/Yellow/Red) with descriptive feedback (e.g., *"Entry is fast! (Under 10 mins)"*).
- **Glassmorphic UI:** A premium, dark-themed command center built with TailwindCSS and Vanilla JS.

### 2. **Context-Aware AI Concierge**
- **Data-Driven Advice:** The AI fetches live sensor data from Firebase before responding to queries.
- **Proactive Routing:** If a zone is congested (>25 min wait), the assistant automatically suggests the fastest alternative (e.g., *"Gate B is currently faster at 5 mins"*).
- **Suggestion Chips:** Quick-action buttons for common queries like *"Which gate is fastest?"* or *"Where is the food court?"*.

### 3. **Crowd Orchestration Engine**
- **Automated Alerts:** A backend simulation engine monitors stadium load and pushes global "Coordination Alerts" to a pulsing notification banner.
- **Proactive Management:** Identifies bottlenecks and advises routing before crowds reach critical levels.

---

## 🛠️ Tech Stack

- **Frontend:** Single-Page Application (HTML5, TailwindCSS CDN, Vanilla JavaScript).
- **Backend:** Python (FastAPI) for AI Concierge logic and Firebase Functions deployment.
- **Database:** Firebase Realtime Database (RTDB) for sub-second synchronization.
- **Simulation:** Python-based Mock Data Engine with `firebase-admin` SDK.

---

## 📦 Project Structure

```text
├── venueflow/
│   ├── frontend/
│   │   └── index.html         # Live Dashboard & AI UI
│   ├── backend/
│   │   ├── main.py            # AI Concierge (Cloud-Native)
│   │   ├── mock_data_gen.py   # Crowd Orchestration Engine
│   │   └── requirements.txt   # Dependencies
├── firebase.json              # Hosting & Functions Config
├── deployment_guide.md        # Step-by-step Cloud Guide
└── README.md                  # You are here
```

---

## ⚡ Quick Start

### 1. Prerequisites
- Python 3.10+
- A Firebase Project with Realtime Database enabled.
- `serviceAccountKey.json` from Firebase placed in `venueflow/backend/`.

### 2. Run the Crowd Simulation
```bash
pip install -r venueflow/backend/requirements.txt
python venueflow/backend/mock_data_gen.py
```

### 3. Launch the AI Concierge
```bash
python venueflow/backend/main.py
```

### 4. View the Dashboard
Simply open `venueflow/frontend/index.html` or host it via Firebase Hosting.

---

## 🌐 Deployment

VenueFlow is optimized for **Firebase Hosting**. 
1. `firebase use <your-project-id>`
2. `firebase deploy --only hosting`

*Note: For full AI Cloud capabilities, the "Blaze" plan is required for Python Functions.*

---

## 🏆 PromptWars Submission
This project focuses on the intersection of **Real-Time Data** and **Proactive AI** to move beyond simple monitoring into active coordination. 

**"Don't just watch the crowd. Flow with it."**
