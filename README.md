# ✈️ Operation Phoenix — Fault-Tolerant Airline Booking System

> A production-grade, full-stack airline booking platform with multi-region AWS deployment, PostgreSQL streaming replication, chaos engineering, and comprehensive service monitoring — built as a DevOps/Cloud Engineering portfolio piece.

[![Python](https://img.shields.io/badge/Backend-Python%20Flask-3776AB?logo=python)](https://flask.palletsprojects.com/)
[![PostgreSQL](https://img.shields.io/badge/Database-PostgreSQL-336791?logo=postgresql)](https://www.postgresql.org/)
[![AWS](https://img.shields.io/badge/Cloud-AWS-FF9900?logo=amazonaws)](https://aws.amazon.com/)
[![Multi-Region](https://img.shields.io/badge/Deployment-Multi--Region-brightgreen)]()

---

## 📌 What Is This Project?

Operation Phoenix simulates a real-world airline IT infrastructure — the kind that powers flight bookings, check-ins, and baggage tracking at scale. Beyond the application itself, it demonstrates **fault-tolerant architecture** with live PostgreSQL database replication across two AWS regions and chaos engineering to verify the system survives regional failures.

---

## 🗺️ Architecture Overview

```
┌─────────────────────────────────────────────────────┐
│                   Users / Passengers                │
└──────────────────────┬──────────────────────────────┘
                       │ HTTPS
┌──────────────────────▼──────────────────────────────┐
│           Flask Application (Python)                │
│   Booking · Check-in · Baggage · Auth · Monitoring  │
└──────┬────────────────────────────────────┬─────────┘
       │                                    │
┌──────▼──────────────┐      ┌──────────────▼──────────────┐
│   US-EAST-1         │      │   US-WEST-2                 │
│   PRIMARY           │─────▶│   REPLICA                   │
│   98.93.226.236     │ stream│   34.218.47.165             │
│   PostgreSQL Master │      │   PostgreSQL Standby        │
│   Flask App         │      │   Flask App                 │
└─────────────────────┘      └─────────────────────────────┘
         │                                │
         └──────────┬─────────────────────┘
                    │
         ┌──────────▼──────────┐
         │  /monitoring/health  │
         │  Per-service checks  │
         │  Business metrics    │
         └──────────────────────┘
```

**Replication Stats:**
- Replication lag: **< 1 second**
- Replication slot: `phoenix_west_slot`
- Status: `streaming` (verified via `pg_stat_replication`)

---

## 🏗️ Core Features

### ✈️ Flight Booking
- Search flights by origin, destination, and date
- Real-time seat availability tracking
- Passenger details capture and booking confirmation
- Auto-generated 6-character booking reference
- Economy, Business, and First Class pricing tiers

### 🛂 Online Check-In
- Check-in by booking reference
- Seat selection
- Boarding pass generation
- Baggage registration at check-in

### 🧳 Baggage Tracking
- End-to-end baggage lifecycle tracking
- Auto-generated baggage tags (`BA######`)
- Real-time status updates: `checked_in → loading → in_transit → arrived`
- Location tracking from check-in counter to destination
- Admin interface for status updates

### 👤 Authentication
- User registration and login
- Password hashing via Werkzeug
- Session management via Flask-Login
- Guest booking supported (no account required)

### 📊 Service Monitoring
Six dedicated health check endpoints, each measuring response time:

| Endpoint | What It Checks |
|---|---|
| `/monitoring/health/database` | DB connectivity + flight count |
| `/monitoring/health/flight-search` | Flight search availability |
| `/monitoring/health/booking` | Booking system + scheduled flights |
| `/monitoring/health/checkin` | Check-in queue accessibility |
| `/monitoring/health/baggage` | Baggage table + tracking |
| `/monitoring/health/authentication` | User table accessibility |
| `/monitoring/health/all` | All services — returns `UP` or `DEGRADED` |

**Business Metrics API** (`/monitoring/metrics/business`):
```json
{
  "total_bookings": 142,
  "total_checkins": 89,
  "pending_checkins": 53,
  "total_users": 34,
  "total_baggage": 201,
  "total_flights": 504,
  "total_revenue": 187432.50
}
```

---

## 🔁 Phase 2: Multi-Region Replication

**Completed:** October 29, 2025

PostgreSQL streaming replication configured between two AWS regions for disaster recovery and high availability.

```sql
-- Primary: verify replica connected
SELECT client_addr, state FROM pg_stat_replication;
-- Result: 34.218.47.165 | streaming

-- Replica: confirm standby mode
SELECT pg_is_in_recovery();
-- Result: t (true)
```

**What was set up:**
- `pg_basebackup` for initial data sync
- Replication slot to prevent WAL segment deletion
- Cross-region VPC networking
- Replication lag monitoring
- Standby promotion runbook

---

## 💥 Chaos Engineering

**AWS Regional Failure Simulation** — verified system behavior under failure conditions:

- Simulated primary region (US-EAST-1) failure
- Verified replica (US-WEST-2) promotion to primary
- Tested application reconnection after failover
- Documented recovery time objectives (RTO)

This phase validates that the architecture survives real-world outages, not just planned deployments.

---

## 🛠️ Tech Stack

| Category | Technology |
|---|---|
| Backend | Python, Flask, Flask-Login, Flask-SQLAlchemy |
| Database | PostgreSQL (streaming replication) |
| Auth | Werkzeug password hashing, Flask-Login sessions |
| Cloud | AWS EC2 (US-EAST-1 + US-WEST-2) |
| Monitoring | Custom health check endpoints, business metrics API |
| Frontend | HTML, Bootstrap, Jinja2 templates |

---

## 🚀 Quick Start

```bash
# Clone the repo
git clone https://github.com/henry-ibe/operation-phoenix.git
cd operation-phoenix

# Set up environment
cp .env.example .env
# Edit .env with your database credentials

# Install dependencies
pip install -r requirements.txt

# Run the app
python app.py
```

**Prerequisites:** Python 3.9+, PostgreSQL 13+

---

## 📁 Repository Structure

```
operation-phoenix/
├── routes/
│   ├── auth.py          # Login, registration, sessions
│   ├── booking.py       # Flight search, booking, check-in, baggage
│   ├── monitoring.py    # Health checks, business metrics
│   └── __init__.py
├── templates/           # Jinja2 HTML templates
├── database/            # DB setup scripts
├── docs/
│   └── PHASE2_MULTI_REGION.md   # Replication architecture
├── models.py            # SQLAlchemy models
├── app.py               # Application entry point
├── requirements.txt
└── .env.example
```

---

## 💡 What This Demonstrates

| Skill | How It's Demonstrated |
|---|---|
| Fault-Tolerant Architecture | Multi-region PostgreSQL streaming replication |
| Chaos Engineering | AWS regional failure simulation and recovery |
| Full-Stack Development | Flask app with auth, booking, baggage, monitoring |
| Database Design | 6 normalized tables with proper relationships |
| Observability | Per-service health checks with response time tracking |
| API Design | RESTful monitoring endpoints with structured JSON |
| DevOps Thinking | Health checks, metrics, disaster recovery planning |

---

## 👤 Author

**Henry Ibe** — Systems & Cloud Infrastructure Engineer
[![GitHub](https://img.shields.io/badge/GitHub-henry--ibe-181717?logo=github)](https://github.com/henry-ibe)

---

*This is a portfolio/lab project. No real passenger data is used or stored.*
