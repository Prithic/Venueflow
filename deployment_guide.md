# VenueFlow Deployment Guide (Firebase)

Follow these steps to push VenueFlow live to Firebase Hosting and Functions.

## 1. Prerequisites
Ensure you are in the project root: `d:\Hackathons\Promptwars\Project`

```bash
# Install Firebase CLI globally
npm install -g firebase-tools

# Login to your Google account
firebase login
```

## 2. Initialize Project
Since we have already created the `firebase.json`, we just need to link the project.

```bash
# Initialize and select 'Hosting' and 'Functions'
# Use the existing 'venueflow-945cc' project
firebase init
```

## 3. Configure Python Environment
Firebase Functions (Python) requires a `requirements.txt` in the function directory.
Ensure `d:/Hackathons/Promptwars/Project/venueflow/backend/requirements.txt` contains:
- `firebase-functions`
- `firebase-admin`

## 4. Deploy
Push the entire stack (Static Frontend + Python Backend) to the cloud.

```bash
# Deploy to the Asian region as configured
firebase deploy
```

## 5. Update Frontend URL (Optional)
Once deployed, Firebase will give you a Hosting URL (e.g., `https://venueflow-945cc.web.app`).
Since we set up a **rewrite** in `firebase.json`, you should update the `fetch` URL in your `index.html` to be relative:

```javascript
// Change this in index.html for production:
const response = await fetch('/chat', { ... }); 
```

---
**Note:** The `mock_data_gen.py` should continue running locally on your machine to push data to the Firebase Realtime Database.
