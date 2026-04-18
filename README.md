# VenueFlow | Stadium Intelligence System

## Chosen vertical
Physical Event Experience

## Approach and logic
The solution utilizes a **Reactive-Proactive hybrid architecture**. 
- **Reactive:** It listens to a Firebase Realtime Database (RTDB) for sub-second updates from simulated crowd sensors.
- **Proactive:** An AI Concierge (RAG-lite) processes these live metrics to provide predictive routing. If a gate's wait time exceeds 25 minutes, the logic automatically recommends the fastest alternative to balance stadium load.

## How the solution works
1. **Data Layer:** A Python-based simulation engine pushes live congestion metrics to Firebase.
2. **Intelligence Layer:** A FastAPI backend queries the live state and appends real-time context to user queries.
3. **Presentation Layer:** A glassmorphic dashboard built with semantic HTML5 provides a high-contrast, accessible interface for attendees.

## Assumptions made
- Stadium zones (Gates, Food Courts) are equipped with IoT occupancy sensors.
- Attendees have mobile access to the dashboard via a local high-density Wi-Fi network.
- The system defaults to the "Fastest Entry" recommendation when no specific query is provided.
