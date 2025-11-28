# 🌍 TerraScout — Multi-Agent Geo-Navigation System

A powerful agent-orchestrated system that transforms location-based queries into **structured, actionable intelligence**.

---

## 🏛️ Architecture — The Agentic Core

Below is a high-level visualization of the TerraScout workflow:

### **🟪 TerraScout (SequentialAgent) — Main Orchestrator**
Controls the overall flow, ensuring every agent runs in the correct order.

---

### **🟥 Context Herald (LlmAgent) — Gatekeeper**
🛑 First checkpoint.  
Rejects non-geo-related queries to save resources and prevent unnecessary computation.

---

### **🟩 Master Navigator Ani (Agent) — Dispatcher**
🗺️ Uses the Maps Tool to locate the **three best candidate locations**, then prepares the parallel workload.

---

### **🟨 Elite Navigators (ParallelAgent) — Deep Searchers**
⚡ Runs *three agents concurrently*, each assigned to one of the target locations.  
They gather rich contextual and geographic insights.

---

### **🟦 Aggregator (Agent) — Finisher**
📦 Combines all navigator results into **clean, standardized JSON** that the frontend can trust.

---

> ⚙️ *The entire workflow is powered by the Agent Development Kit (ADK), mixing Sequential & Parallel agents for maximum efficiency.*

---

## ✨ Key Features

| Feature | Description |
|--------|-------------|
| ⚡ **Contextual Filtering** | Context Herald blocks irrelevant queries before ADK agents activate. |
| 🔀 **Parallel Processing** | Elite Navigators work simultaneously to reduce search time. |
| 🧩 **Structured Output** | Guarantees predictable JSON for stable frontend rendering. |
| 💾 **Persistent History** | All conversations saved in SQLite using SQLAlchemy ORM. |
| ✔️ **CORS-Enabled API** | Fully configured FastAPI backend prevents 405 CORS issues. |

---

## 🧭 System Overview

