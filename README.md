# Survivalence — Real-Time Surveillance System

A production-grade, asynchronous video surveillance platform built with Python, FastAPI, and YOLOv8. Detects objects in real time, tracks them across frames, enforces configurable restricted zones, and delivers instant alerts via Telegram.

---

## Features

- **Real-time object detection** using YOLOv8 nano (~30 fps on CPU)
- **IoU-based object tracking** — persistent track IDs across frames
- **Zone intrusion detection** — JSON-configurable restricted areas with 30-second cooldown
- **Live MJPEG stream** — view annotated video in any browser
- **REST API** — detections, alerts, and statistics endpoints with Swagger docs
- **Telegram notifications** — instant alerts on zone violations
- **Automatic IMS integration** — creates incidents in the Incident Management System
- **PostgreSQL persistence** — full audit trail of detections and alerts

---

## Tech Stack

| Layer | Technology |
|---|---|
| Web framework | FastAPI 0.111 + Uvicorn |
| Object detection | Ultralytics YOLOv8 nano |
| Image processing | OpenCV 4.9 |
| Database | PostgreSQL + SQLAlchemy 2.0 (async) + asyncpg |
| Migrations | Alembic |
| HTTP client | httpx (Telegram + IMS) |
| Config | pydantic-settings + python-dotenv |
| Language | Python 3.11 |

---

## Architecture

```
Camera (webcam / video file / RTSP)
    │
    ▼
SurveillancePipeline  (asyncio background task)
    ├── Detector      YOLOv8 inference  (thread pool executor)
    ├── Tracker       IoU-based object association
    ├── ZoneChecker   bbox overlap with restricted zones
    ├── Visualizer    frame annotation
    └── AlertService  cooldown-aware alert creation
         ├── Telegram notification
         └── IMS HTTP POST → auto incident creation
    │
    ▼
PostgreSQL                    FrameStore (thread-safe JPEG buffer)
(cameras, tracked_objects,          │
 detections, alerts)                ▼
    │                     MJPEG Stream  /api/v1/stream/video
    ▼
REST API  /api/v1/{detections, alerts, stats}
```

---

## Database Schema

```
cameras          → tracked_objects → detections
                                   → alerts
```

- **cameras** — camera configuration and source URL
- **tracked_objects** — persistent object identities (first\_seen, last\_seen, is\_active)
- **detections** — per-frame bounding box records (class, confidence, bbox)
- **alerts** — zone violation events with cooldown and resolution status

---

## Prerequisites

- Python 3.11+
- PostgreSQL 14+
- Webcam or video file

---

## Installation

```bash
# 1. Clone the repository
git clone https://github.com/AnLayz/survivalence.git
cd survivalence

# 2. Create and activate virtual environment
python -m venv venv
venv\Scripts\activate        # Windows
# source venv/bin/activate   # Linux/macOS

# 3. Install dependencies
pip install -r requirements.txt

# 4. Create PostgreSQL database
psql -U postgres -c "CREATE DATABASE survivalence;"

# 5. Copy and configure environment variables
cp .env.example .env
# Edit .env with your values
```

---

## Configuration

Create a `.env` file in the project root:

```env
# Database
DATABASE_URL=postgresql+asyncpg://postgres:yourpassword@localhost:5432/survivalence

# Computer Vision
YOLO_MODEL_PATH=models_weights/yolov8n.pt
CAMERA_SOURCE=0          # 0 = webcam, or path to video file / RTSP URL
CONFIDENCE_THRESHOLD=0.5

# Telegram (optional)
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=your_chat_id

# IMS Integration (optional)
IMS_URL=http://localhost:8000
IMS_USERNAME=surveillance_bot
IMS_PASSWORD=your_password
```

---

## Zone Configuration

Edit `zones/camera_1.json` to define restricted areas:

```json
[
  {
    "id": "zone_a",
    "name": "Restricted Entry",
    "type": "restricted",
    "x": 100,
    "y": 100,
    "width": 400,
    "height": 300
  }
]
```

---

## Running

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload
```

| URL | Description |
|---|---|
| `http://localhost:8001/docs` | Swagger API documentation |
| `http://localhost:8001/api/v1/stream/` | Live MJPEG stream viewer |
| `http://localhost:8001/api/v1/alerts/` | Zone violation alerts |
| `http://localhost:8001/api/v1/detections/` | Recent detections |
| `http://localhost:8001/api/v1/stats/` | System statistics |

---

## API Endpoints

| Method | Endpoint | Description |
|---|---|---|
| GET | `/api/v1/detections/` | Recent detection records with bounding boxes |
| GET | `/api/v1/alerts/` | Zone violation alerts |
| GET | `/api/v1/stats/` | Total detections, alerts, active objects |
| GET | `/api/v1/stream/video` | Live MJPEG video stream |
| GET | `/api/v1/stream/` | HTML stream viewer |
| GET | `/health` | Health check |

---

## Project Structure

```
survivalence/
├── app/
│   ├── main.py                 # FastAPI app + lifespan
│   ├── api/
│   │   ├── deps.py             # Dependency injection
│   │   └── routes/
│   │       ├── alerts.py       # Alerts endpoint
│   │       ├── detections.py   # Detections endpoint
│   │       ├── stats.py        # Statistics endpoint
│   │       └── stream.py       # MJPEG stream
│   ├── core/
│   │   └── config.py           # Settings (pydantic-settings)
│   ├── cv/
│   │   ├── detector.py         # YOLOv8 wrapper
│   │   ├── tracker.py          # IoU-based tracker
│   │   ├── zone_checker.py     # Zone intrusion logic
│   │   ├── visualizer.py       # Frame annotation
│   │   ├── frame_store.py      # Thread-safe JPEG buffer
│   │   └── pipeline.py         # Main surveillance loop
│   ├── database/
│   │   ├── base.py             # SQLAlchemy declarative base
│   │   └── session.py          # Async engine + session
│   ├── models/                 # SQLAlchemy ORM models
│   │   ├── camera.py
│   │   ├── tracked_object.py
│   │   ├── detection.py
│   │   └── alert.py
│   └── services/
│       ├── alert_service.py    # Alert creation + cooldown
│       ├── detection_service.py
│       ├── telegram_service.py # Telegram notifications
│       └── ims_service.py      # IMS integration
├── zones/
│   └── camera_1.json           # Zone definitions
├── models_weights/
│   └── yolov8n.pt              # YOLOv8 nano weights
├── alembic/                    # Database migrations
├── tests/
├── .env.example
├── requirements.txt
└── README.md
```

---

## Integration with IMS

When a zone violation alert fires, the system automatically creates an incident in the [Incident Management System](https://github.com/AnLayz/incident-management-system):

```
Zone violation detected
    → Alert saved to PostgreSQL
    → Telegram notification sent
    → HTTP POST to IMS /api/v1/incidents/
        title:     "Zone Intrusion - Camera #1"
        severity:  "high"
        camera_id: 1
        alert_id:  42
```

The IMS service account (`surveillance_bot`) is created automatically when the IMS starts.

---
