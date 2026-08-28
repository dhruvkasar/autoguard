# AutoGuard – Project Plan & Specification

**Project:** AI-Powered Retail Theft, Violence & Threat Prevention System  
**Version:** 1.0  
**Last Updated:** 2026-08-26  
**Status:** In Development – MVP Phase  

---

## 1. Project Overview

### Problem Statement
Retail stores cannot effectively monitor multiple CCTV feeds simultaneously, leading to:
- **Theft & shrinkage risk:** Missed shoplifting, delayed response, human fatigue
- **Violence & safety risk:** Armed robbery, threats, altercations escalate faster than manual monitoring can respond

### Solution Vision
An affordable, open-source, AI-assisted surveillance system that:
- Watches all camera feeds simultaneously and tirelessly
- Detects theft-indicative behavior AND violence/weapon threats in real time
- Auto-captures visual evidence with AI-generated descriptions
- Pushes instant alerts to staff mobile apps
- Keeps humans firmly in the decision loop (no automated punishment)

### Target Users
- **Primary:** Small/medium retail store managers and security staff
- **Secondary:** Store owners, law enforcement (evidence handover)

---

## 2. System Architecture

### High-Level Flow
```
CCTV/IP Cameras 
  → Edge Layer (Video Processing + Detection + Tracking + Behavior Analysis)
  → Core Server (AI Agent + Evidence Store + Pairing Service + Alert Dispatcher + REST API)
  → Client Layer (Web Dashboard + Mobile App)
```

### Component Layers

**Edge Layer (Store PC / Raspberry Pi):**
- Video capture (OpenCV)
- Person detection (YOLOv8)
- Person tracking (ByteTrack)
- Zone-based behavior analysis
- Local rule engine

**Core Server (Store PC / Small Server / Cloud VM):**
- AI description generator (template-based + optional Ollama LLM)
- Evidence storage (AES-256 encrypted)
- Pairing service (code-based device registration)
- Alert dispatcher (Push/Telegram/Email)
- REST API (Flask → FastAPI migration planned)
- Security dashboard backend

**Client Layer:**
- Web dashboard (manager/owner)
- Mobile app (React Native - staff/security)

---

## 3. Functional Requirements

### 3.1 Camera Input & Detection
- ✅ Accept webcam, IP camera (RTSP), or CCTV feed
- ✅ YOLOv8 person detection with configurable confidence threshold
- ✅ ByteTrack multi-person tracking with unique session IDs
- MVP: Single camera (architecture supports multi-camera)

### 3.2 Zone Management
- ✅ Three configurable zones: Shelf, Checkout, Exit
- ✅ Interactive zone calibrator tool
- Zone coordinates stored in `config/config.yaml`

### 3.3 Theft-Indicative Detection Rules
- ✅ **Loitering:** Dwell time in shelf zone exceeds threshold (default: 5s for demo)
- ✅ **Repeated Shelf-Exit Movement:** Back-and-forth pattern within time window
- ✅ **Exit Without Checkout:** Movement from shelf → exit, skipping checkout zone
- All thresholds configurable via YAML

### 3.4 Violence & Threat Detection Rules (IN PROGRESS)
- ⚠️ **Aggressive pose detection:** MediaPipe/OpenPose skeletal keypoints (NOT YET IMPLEMENTED)
- ⚠️ **Rapid clustering/dispersal:** Sudden multi-person movement vectors (NOT YET IMPLEMENTED)
- ⚠️ **Elevated object detection:** Long/rigid handheld objects in raised posture (NOT YET IMPLEMENTED)
- ⚠️ **Group freeze posture:** Multiple people static simultaneously (NOT YET IMPLEMENTED)
- All violence rules tagged HIGH PRIORITY (bypass alert cooldown)

### 3.5 AI Description Generator
- ⚠️ **Current:** Only rule names sent in alerts
- ⚠️ **Required:** Natural language generation (template-based minimum)
- Example: "Person ID 14 remained in electronics aisle for 52 seconds with repeated hand-to-pocket motion; flagged as possible concealment behavior."

### 3.6 Evidence Capture & Storage
- ✅ Auto-capture image snapshot on rule trigger
- ✅ SHA-256 hash for integrity verification
- ✅ Metadata: timestamp, camera ID, track ID, rule triggered
- ✅ Evidence verifier tool (`verify_evidence.py`)
- ⚠️ AES-256 encryption at rest (NOT YET IMPLEMENTED)
- ⚠️ Tamper-evident hash chain log (NOT YET IMPLEMENTED)

### 3.7 Alert System
- ✅ Telegram bot integration (immediate fallback)
- ✅ Alert cooldown (per rule + track ID)
- ✅ Daily alert cap
- ✅ Local audio beep alerts (Windows)
- ⚠️ Mobile push notifications via FCM (NOT YET IMPLEMENTED)
- ⚠️ Email alerts (NOT YET IMPLEMENTED)

### 3.8 Mobile App & Pairing Flow
- ❌ React Native mobile app (NOT STARTED)
- ❌ Manager-generated 6-digit pairing codes (NOT STARTED)
- ❌ Device registration with JWT tokens (NOT STARTED)
- ❌ Push notification handling (NOT STARTED)
- ❌ Incident acknowledgment/false-alarm marking (NOT STARTED)

### 3.9 Security Dashboard (Web)
- ⚠️ Basic Flask server exists with evidence viewer
- ⚠️ Missing: Live camera view, incident timeline, device management UI
- ⚠️ Missing: Rule threshold configuration UI
- ⚠️ Missing: Manager-only actions (generate pairing codes, export evidence)

---

## 4. Technology Stack (100% Open Source)

| Component | Technology | Status |
|-----------|-----------|--------|
| Person Detection | YOLOv8 (Ultralytics, AGPL-3.0) | ✅ Implemented |
| Tracking | ByteTrack (supervision library) | ✅ Implemented |
| Pose Estimation | MediaPipe / OpenPose | ❌ Not Started |
| Video Processing | OpenCV | ✅ Implemented |
| AI Description | Template-based + Ollama (optional) | ⚠️ Template only, not integrated |
| Backend | Flask → FastAPI (planned) | ⚠️ Basic Flask only |
| Database | SQLite (MVP) → PostgreSQL (production) | ❌ Not Started |
| Evidence Encryption | Cryptography (Python) | ❌ Not Started |
| Mobile App | React Native (Expo) | ❌ Not Started |
| Push Notifications | Firebase Cloud Messaging (free tier) | ❌ Not Started |
| Deployment | Docker + Docker Compose | ❌ Not Started |

---

## 5. Security & Privacy Architecture

### Data Classification
**Sensitive Data:**
- Raw video frames and snapshots (biometric-adjacent)
- Incident metadata (timestamps, zones, behavior flags)
- Device pairing tokens and staff identifiers

### Security Controls
- ⚠️ **Transport:** TLS 1.3 for all API/dashboard traffic (NOT YET IMPLEMENTED)
- ⚠️ **At Rest:** AES-256 for stored snapshots/clips (NOT YET IMPLEMENTED)
- ⚠️ **Access Control:** Role-based (Manager vs Staff), server-side enforcement (NOT YET IMPLEMENTED)
- ⚠️ **Retention:** Auto-deletion after configurable window (basic retention_days in config, but no enforcement yet)
- ✅ **No Third-Party Sharing:** All AI processing runs on-premise

### Threat Mitigation
- ⚠️ Pairing code brute force → short expiry, single-use, rate limiting (NOT YET IMPLEMENTED)
- ⚠️ Stolen device → manager revokes token (NOT YET IMPLEMENTED)
- ⚠️ Insider misuse → tamper-evident audit log (NOT YET IMPLEMENTED)

---

## 6. MVP Scope

### ✅ INCLUDED (Build These)
- Single camera feed
- Person detection & tracking
- Rule-based theft logic (3 rules)
- Rule-based violence/threat logic (4 rules) **← HIGH PRIORITY GAP**
- Template-based AI description generation **← HIGH PRIORITY GAP**
- Image snapshot evidence with encryption **← PARTIAL: no encryption yet**
- Mobile app pairing via code **← NOT STARTED**
- Push + Telegram fallback alerts **← PARTIAL: Telegram only**
- Basic web dashboard **← PARTIAL: very basic**

### ❌ EXCLUDED (Do Not Build Unless Requested)
- Facial recognition / repeat-offender identity matching
- Multi-camera correlation and heatmaps
- POS / inventory system integration
- Automated environmental response (alarms, door locks, police API)
- Cloud multi-tenant deployment

---

## 7. Success Metrics (MVP Acceptance Criteria)

| Metric | Target | Current Status |
|--------|--------|----------------|
| End-to-end detection latency | < 3 seconds | ✅ ~1-2 seconds |
| Alert delivery latency | < 5 seconds | ✅ ~2-3 seconds (Telegram) |
| False positive rate | < 30% (MVP acceptable) | ⚠️ Not measured yet |
| System uptime (8-hour shift) | > 95% | ⚠️ Not tested |
| Evidence integrity verification | 100% verifiable | ✅ SHA-256 implemented |
| Mobile app pairing success | > 90% first attempt | ❌ N/A (not built) |

---

## 8. Key Design Decisions

### Decision Log

**D1: Zone-based detection over whole-frame analysis**  
- **Rationale:** Simpler, faster, more explainable; sufficient for MVP
- **Trade-off:** Less sophisticated than ML-based anomaly detection
- **Status:** Implemented, working well

**D2: ByteTrack over DeepSORT**  
- **Rationale:** Better performance, simpler, actively maintained
- **Trade-off:** None identified for this use case
- **Status:** Implemented

**D3: Telegram as primary alert channel for MVP**  
- **Rationale:** Zero infrastructure cost, instant delivery, easy testing
- **Trade-off:** Requires staff to have Telegram installed
- **Status:** Implemented and working
- **Future:** Add FCM push for mobile app

**D4: Template-based NLG before LLM**  
- **Rationale:** Deterministic, zero hallucination risk, faster
- **Trade-off:** Less natural language, more rigid
- **Status:** Decided, not yet implemented

**D5: Flask → FastAPI migration planned**  
- **Rationale:** Better async support, built-in OpenAPI docs, modern
- **Trade-off:** Migration effort
- **Status:** Deferred until core features stable

**D6: Single-camera MVP, multi-camera architecture**  
- **Rationale:** Reduces complexity, architecture supports scaling
- **Status:** Single camera implemented

---

## 9. Open Questions & Risks

### Technical Risks
- **R1:** Violence detection accuracy with rule-based pose analysis (HIGH)
  - Mitigation: Position as "assistive flag for human review," not certified detection
  - Status: Not yet implemented to assess

- **R2:** False positive rate on theft rules with low demo thresholds (MEDIUM)
  - Mitigation: Make all thresholds easily configurable
  - Status: Thresholds configurable, need real-world tuning

- **R3:** Mobile app pairing UX complexity (MEDIUM)
  - Mitigation: Follow familiar Smart-TV pairing pattern
  - Status: Not yet built

### Open Questions
- **Q1:** Which pose estimation library? MediaPipe (easier) vs OpenPose (more accurate)
  - **Decision needed:** By Week 4 start
  
- **Q2:** Self-hosted ntfy.sh vs Firebase FCM for push?
  - **Decision needed:** By Week 6 start
  
- **Q3:** Docker Compose vs manual setup for demo/interview?
  - **Decision:** Docker Compose strongly preferred for reproducibility

---

## 10. Repository Structure

```
D:\Major Project\
├── config/
│   └── config.yaml              # All non-secret configuration
├── docs/
│   └── modules/                 # Per-module documentation
│       ├── edge.md              # Video pipeline + detection
│       ├── ai-agent.md          # Description generator
│       ├── backend.md           # API + pairing + evidence
│       ├── dashboard.md         # Web UI
│       ├── mobile.md            # React Native app
│       └── infra.md             # Docker + deployment
├── src/                         # Python edge/backend code
│   ├── main.py                  # Entry point
│   ├── detector.py              # YOLOv8 wrapper
│   ├── tracker.py               # ByteTrack wrapper
│   ├── zones.py                 # Zone management
│   ├── rules.py                 # Behavior engine
│   ├── evidence.py              # Evidence capture/storage
│   ├── alerts.py                # Telegram alerter
│   ├── server.py                # Flask evidence viewer
│   ├── config_loader.py         # YAML config loader
│   ├── logging_config.py        # Logging setup
│   ├── zone_calibrator.py       # Interactive zone tool
│   └── verify_evidence.py       # Integrity checker
├── tests/                       # Unit & integration tests
│   └── test_rules.py            # Rule engine tests
├── evidence/                    # Encrypted snapshots + metadata
├── logs/                        # Audit logs
├── .env.example                 # Environment template
├── requirements.txt             # Python dependencies
├── plan.md                      # This file
├── howmuchworkdone.md           # Progress tracking
└── README.md                    # User-facing documentation
```

---

## 11. Definition of Done (Checklist for Every Feature)

A task is complete when:
- [ ] Code runs via `docker-compose up` (or documented manual setup)
- [ ] Relevant unit/integration tests exist and pass
- [ ] Security requirements met (TLS, encryption, auth, input validation, no secrets committed)
- [ ] Human-in-the-loop framing intact in UI copy, API responses, logs
- [ ] Owning module's `docs/modules/*.md` updated
- [ ] `howmuchworkdone.md` task checked off with brief note
- [ ] Architecture/scope changes reflected in this `plan.md`

---

## 12. Next Steps (Priority Order)

### Immediate (For Mock Interview Preparation)
1. ✅ Create `plan.md` and `howmuchworkdone.md`
2. Create module documentation (`docs/modules/*.md`)
3. Add AI description generator (template-based)
4. Docker Compose setup for one-command deployment
5. Improve web dashboard UI

### High Priority (Core MVP Gaps)
6. Implement violence/threat detection rules (pose-based)
7. Add AES-256 evidence encryption
8. Basic mobile app with pairing flow
9. REST API with JWT authentication
10. Comprehensive test suite

### Medium Priority (Polish & Production-Ready)
11. FastAPI migration
12. TLS/HTTPS enforcement
13. Tamper-evident audit logging
14. Multi-camera support
15. Cloud deployment guide

---

**Last Updated:** 2026-08-26 by AI Agent  
**Next Review:** Before starting Week 4 tasks
