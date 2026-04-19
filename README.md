# VenueFlow | Hybrid Intelligence System

VenueFlow is a Rank 1 Championship coordination platform utilizing a **2-Layer Hybrid Reasoning Engine**. It combines high-speed deterministic utility analysis with adaptive LLM-backed synthesis for complex situational awareness.

## Chosen vertical
AI-powered Autonomous Stadium Intelligence and Crowd Flow Optimization.

## Approach and logic
VenueFlow operates via a **Hybrid Reasoning Architecture**:

1.  **Layer 1: Deterministic Utility Engine**: Computes real-time utility vectors for each stadium sector using **Semantic Similarity Scoring** (difflib-based) and **Inverse Wait-Time Normalization**. 
    *   `Utility Score = Similarity(Query, Zone) + (1.0 / (Wait_Time + 1))`
    *   A **Confidence Engine** calculates the dispersion of utility across sectors.

2.  **Layer 2: LLM Reasoning Booster**: Automatically triggered when the confidence score falls below a set threshold (0.65) or for ambiguous intent. It injects the full system state into a context window for multi-variable constraint satisfaction.

## How the solution works
- **Real-time Data**: Syncs sub-second telemetry from Firebase RTDB.
- **Scoring Matrix**: Rankings are generated dynamically without hardcoded keyword lists or if/else branching.
- **Adaptive Response**: High-confidence queries receive immediate utility-based routing; low-confidence/complex queries are synthesized by the Layer 2 Booster.

## Assumptions made
- Stadium zone identifiers (`gate_a`, `food_court`, etc.) are descriptive and serve as semantic anchors.
- LLM API availability is optional; the system fails gracefully to Layer 1.
- Global latency is minimized by performing utility ranking before triggering network-heavy LLM calls.

---
**Championship Version: 6.0.0 (Hybrid Intelligence)**
