![Docker](https://github.com/CIARC-CUIYC/Palantiri/actions/workflows/build-docker.yaml/badge.svg)
[![Checked with mypy](https://www.mypy-lang.org/static/mypy_badge.svg)](https://mypy-lang.org/)
# 🔮 Palantíri SIL Framework

**Palantíri** (Quenya plural of *Palantír*, “far-seer”) is a Python-based **Software-in-the-Loop (SIL)** simulation framework 
developed to emulate the backend system provided by ESA for CIARC 2024/25.

The framework simulates MELVIN’s internal
state and trajectory, and enables both control and observation of the simulation via API endpoints built with Flask.
In addition, it accurately models beacons and zones—both known and secret—along with their dynamic states.

---

## 🧰 Features

- 🛰️ Accurate CIARC simulation physics modeling
- 🌐 REST API for observation and control of MELVIN satellite
- ⏰️ Time-aware simulation with custom clock
- 🔊 Real-time SSE (Server-Sent Events) for beacon pings
- 🎯 Objective management: zoned & beacon-based
- ⚡  Lightweight Flask backend for easy integration with external systems
---

## 📁 Folder Structure

```
src/
├── __main__.py               # Entry point for simulation
├── app/
│   ├── models/               # models for MEVLVN stats and objective management
│   │   ├── melvin.p
│   │   ├── obj_manager.py
│   │   ├── obj_zoned.py
│   │   ├── obj_beacon.py
│   ├── routes/               # Flask blueprints
│   ├── helpers.py            # Vector math, constraints, validation
│   ├── constants.py
│   └── sim_clock.py
```

---

## 🛰️ Core Components

### **models (`app/models`)**
- `melvin.py`: Simulates satellite movement, enforcing acceleration constraints, velocity bounds, and fuel consumption.
Can receive target velocity and gradually apply it in validated steps.
- `obj_manager.py`: Simulates backend behavior in objective management for both beacon and zoned obj

### **Flask Endpoints (app/routes`)**
- `GET /announcements`: SSE stream emitting beacon pings
- `PUT /beacon`: Submission of Beacon Position estimate
- `PUT /control`: Command a new target velocity and camera state
- `GET|PUT|DELETE /objective`: Manage objectives manually or randomly
- `GET /observation`: Returns MELVIN’s current telemetry
- `GET /reset`: Resets simlulation



---

## 🔨 Setup Instructions

1. **Clone the repo**
   ```bash
   git clone  https://github.com/CIARC-CUIYC/Palantiri.git
   cd Palantiri
   ```

2. **Create and activate virtual environment**
   ```bash
   python3.11 -m venv .venv
   source .venv/bin/activate
   ```

3. **Install palantiri dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the simulation**
   ```bash
   python -m src
   ```
---
## ⚙️ Configuration of PUT /objective
Differing from the PUT command at the /objective endpoint of the actual CIARC backend that commanding of the Palantiri
endpoint differs slightly
```json
{

  "num_random_zoned": 0,      // required field
  "num_random_beacon": 0,     // required field
  "zoned_objectives": [       // optional field, [] if empty
    {
        "id": 1,
        "name": "Precise Picture 10",
        "start": "2025-03-29T12:10:00Z",
        "end": "2025-03-29T16:10:00Z",
        "decrease_rate": 0.99,
        "zone": [
            12465,
            8935,
            13065,
            9535
        ],
        "optic_required": "narrow",
        "coverage_required": 1.0,
        "description": "Scout the land between the mountains. Something stirs in the shadows",
        "sprite": null,
        "secret": false
        }
  ],                          // optional field, [] if empty
  "beacon_objectives": [      
    {
        "id": 2,
        "name": "EBT 2",
        "start": "2025-03-29T9:10:00Z",
        "end": "2025-03-29T13:00:00Z",
        "decrease_rate": 0.99,
        "attempts_made": 0,
        "description": "The Beacon 2 is lit! Gondor calls for aid!",
        "beacon_height": 5721,
        "beacon_width": 8300
    }
  ]     // optional

}
```
---
## 🐳 Containerized SIL Deployment
To run MELVIN-OB inside the Cirdan container environment (with the SIL framework):
```bash
git clone https://github.com/CIARC-CUIYC/cirdan.git
cd cirdan
docker compose up --build
```
This setup includes:
* [melvin-ob](https://github.com/CIARC-CUIYC/melvin-ob) in a terminal-accessible tmux session
* Palantíri SIL backend (exposes REST API)

See detailed instructions [here](https://github.com/CIARC-CUIYC/cirdan).







