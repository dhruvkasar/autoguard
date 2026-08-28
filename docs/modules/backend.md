# Backend Module – API, Evidence Storage, Alerts & Pairing

**Module:** Backend/Core Server Layer  
**Status:** ⚠️ Partial (basic Flask server, Telegram alerts, evidence storage - no encryption/auth yet)  
**Last Updated:** 2026-08-26  
**Owner:** Cybersecurity Final Year Project Team

---

## Purpose

The Backend module provides server-side services for the AutoGuard system including evidence storage, alert dispatching, device pairing (planned), and API endpoints for the dashboard and mobile app. It acts as the central coordinator between the edge detection layer and client applications.

**Key Responsibilities:**
- Store evidence (snapshots + metadata) with integrity verification
- Dispatch alerts via multiple channels (Telegram, push notifications, email)
- Manage device pairing and authentication (planned)
- Expose REST API for dashboard and mobile app
- Handle evidence encryption and audit logging (planned)
- Enforce role-based access control (planned)

---

## Architecture

```
Edge Layer (main.py)
  ↓ calls
Evidence Module → saves encrypted snapshots (planned)
Alerts Module → dispatches to Telegram/FCM/Email
  ↓
Backend API (Flask → FastAPI planned)
  ↓ serves
Web Dashboard + Mobile App
```

**Current State:** Basic services exist, but no proper API structure, authentication, or encryption yet.

---

## Public Interfaces

### Evidence Storage

**File:** `src/evidence.py`

**Function:** `save_evidence(frame: np.ndarray, bbox: np.ndarray, track_id: int, rule: str, evidence_dir: str, camera_id: str, logger) -> str`
- Saves snapshot image and metadata JSON for a rule trigger event
- **Parameters:**
  - `frame`: OpenCV frame (full camera view)
  - `bbox`: Bounding box [x1, y1, x2, y2] of detected person
  - `track_id`: ByteTrack tracking ID
  - `rule`: Rule name that triggered (e.g., "Loitering in Shelf Zone")
  - `evidence_dir`: Directory path for evidence storage
  - `camera_id`: Camera identifier string
  - `logger`: Logger instance
- **Returns:** Path to saved image file
- **Side Effects:** 
  - Writes `.jpg` image file to `evidence/` directory
  - Writes `.json` metadata file with same basename
  - Computes SHA-256 hash of image and stores in metadata

**Metadata JSON Schema:**
```json
{
  "timestamp": "2026-08-26T10:23:40Z",
  "camera_id": "CAM01",
  "track_id": 42,
  "rule": "Loitering in Shelf Zone",
  "bbox": [120, 340, 280, 650],
  "sha256": "abc123...def789",
  "image_path": "evidence/CAM01_20260826_102340_ID42.jpg"
}
```

**Function:** `prune_old_evidence(evidence_dir: str, retention_days: int, logger) -> None`
- Deletes evidence older than retention period
- **Parameters:**
  - `evidence_dir`: Directory to scan
  - `retention_days`: Age threshold (files older than this are deleted)
  - `logger`: Logger instance
- **Returns:** None
- **Side Effects:** Deletes matching `.jpg` and `.json` files
- **Status:** ⚠️ Function exists but not called automatically (manual trigger only)

---

### Evidence Verification

**File:** `src/verify_evidence.py`

**CLI Tool:** Verifies integrity of evidence by recomputing SHA-256 hashes

**Usage:**
```powershell
python -m src.verify_evidence --dir evidence
```

**Output:**
- Lists all evidence files
- Recomputes SHA-256 hash of each image
- Compares to stored hash in metadata JSON
- Reports PASS/FAIL for each file

**Status:** ✅ Working, useful for demonstrating tamper detection

---

### Alert Dispatching

**File:** `src/alerts.py`

**Class:** `TelegramAlerter`
- Sends photo alerts via Telegram Bot API
- **Constructor:** `__init__(enabled: bool, token: str, chat_ids: list, camera_id: str, logger)`
  - `enabled`: Master switch (from config)
  - `token`: Telegram bot token (from .env)
  - `chat_ids`: List of Telegram chat IDs to notify (from .env)
  - `camera_id`: Camera identifier for caption
  - `logger`: Logger instance
- **Method:** `send_photo(image_path: str, caption: str) -> bool`
  - **Parameters:** 
    - `image_path`: Path to evidence snapshot
    - `caption`: Alert text (rule name + timestamp + camera ID)
  - **Returns:** True if sent successfully, False otherwise
  - **Behavior:** 
    - Sends photo to all configured chat IDs
    - Logs success/failure per chat ID
    - Continues sending to remaining IDs if one fails
    - Silently skips if `enabled=False`

**Environment Variables Required:**
```
TELEGRAM_BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
TELEGRAM_CHAT_IDS=123456789,987654321  # Comma-separated
```

**Configuration (config.yaml):**
```yaml
alerts:
  enabled: true
  camera_id: "CAM01"
  cooldown_seconds: 15      # Min time between alerts for same rule+track_id
  daily_cap: 50             # Max alerts per day (prevents spam)
```

**Alert Hygiene Logic (in main.py):**
- **Cooldown:** Prevents duplicate alerts for same (rule, track_id) pair within N seconds
- **Daily Cap:** Global limit on alerts per calendar day
- **Implementation:** In-memory dicts (resets on restart)

**Status:** ✅ Telegram working well, ❌ Push notifications (FCM) not implemented, ❌ Email fallback not implemented

---

### Configuration Loader

**File:** `src/config_loader.py`

**Function:** `load_config() -> dict`
- Loads configuration from `config/config.yaml` and `.env`
- **Returns:** Merged configuration dict
- **Behavior:**
  - Loads YAML config file
  - Loads .env file via python-dotenv
  - Injects environment variables into config where needed (e.g., Telegram credentials)
  - Validates required fields (basic checks only)
- **Status:** ✅ Working

**Separation of Concerns:**
- `config.yaml`: Non-secret configuration (thresholds, zones, paths)
- `.env`: Secrets only (Telegram token, API keys, database passwords)
- **Never commit .env to git** (.gitignore enforced)

---

### Logging & Audit Trail

**File:** `src/logging_config.py`

**Function:** `setup_logging(log_dir: str = "logs") -> logging.Logger`
- Configures structured logging for audit trail
- **Returns:** Logger instance
- **Behavior:**
  - Creates `logs/app.log` file
  - Format: `[timestamp] [level] message`
  - Logs to both file and console
  - Automatic log rotation (not yet implemented, TODO)

**Logged Events:**
- ✅ System start/stop
- ✅ Detection rule triggers (rule name, track ID, timestamp)
- ✅ Evidence saved (file path, hash)
- ✅ Alerts sent (channel, success/failure)
- ✅ Zone transitions (if debug.verbose enabled)
- ❌ Evidence views/exports (not implemented yet - needs tamper-evident log)
- ❌ Pairing events (not implemented yet)
- ❌ Configuration changes (not implemented yet)

**Status:** ⚠️ Basic logging works, but not tamper-evident (hash chain planned Week 7)

---

### REST API (Basic Flask Server)

**File:** `src/server.py`

**Current Implementation:** Very basic Flask app for evidence viewing

**Endpoints:**

**`GET /`**
- Returns simple HTML instructions page
- No authentication required (local demo only)

**`GET /evidence`**
- Returns JSON array of all evidence files
- **Response Schema:**
```json
[
  {
    "image": "CAM01_20260826_102340_ID42.jpg",
    "metadata": "CAM01_20260826_102340_ID42.json",
    "timestamp": "2026-08-26T10:23:40Z",
    "rule": "Loitering in Shelf Zone",
    "camera_id": "CAM01",
    "track_id": 42
  }
]
```

**`GET /evidence/image?path=<filename>`**
- Serves evidence image file
- **Query Parameters:** `path` (filename only, not full path)
- **Response:** JPEG image with appropriate Content-Type header
- **Security:** ⚠️ No path traversal protection (accepts any filename)

**`GET /dashboard`**
- Returns HTML page with evidence thumbnails in a grid
- **Features:** 
  - Thumbnail grid (3 columns)
  - Shows rule name and timestamp per image
  - Click to view full size
- **Status:** ✅ Works but very basic UI

**Authentication (Current):**
- Optional role-based tokens via environment variables:
  - `ADMIN_TOKEN` - Full access
  - `SECURITY_TOKEN` - View evidence
  - `VIEWER_TOKEN` - Read-only
- Tokens checked via `Authorization: Bearer <token>` header
- **Status:** ⚠️ Basic implementation, not production-ready

**Status:** ⚠️ Flask server works for demo but needs complete rebuild for MVP:
- ❌ No proper REST API structure
- ❌ No JWT authentication
- ❌ No role-based access control enforcement
- ❌ No input validation/sanitization
- ❌ No rate limiting
- ❌ No TLS/HTTPS
- ❌ No pairing endpoints
- ❌ No evidence export functionality

**Planned Migration:** Flask → FastAPI (Week 7)
- Better async support
- Built-in OpenAPI documentation
- Modern dependency injection
- Better WebSocket support for live video

---

## Key File Paths

```
src/evidence.py              # Evidence capture and storage
src/alerts.py                # Telegram alerter (FCM planned)
src/server.py                # Basic Flask API (FastAPI planned)
src/config_loader.py         # YAML + .env loader
src/logging_config.py        # Logging setup
src/verify_evidence.py       # SHA-256 integrity checker (CLI tool)
evidence/                    # Stored snapshots (.jpg + .json pairs)
logs/app.log                 # Audit log
config/config.yaml           # Non-secret configuration
.env                         # Secrets (NOT in git)
.env.example                 # Template for .env
```

---

## Configuration

**File:** `config/config.yaml`

```yaml
storage:
  evidence_dir: evidence
  logs_dir: logs
  retention_days: 7          # Prune evidence older than N days

alerts:
  enabled: true
  camera_id: "CAM01"
  cooldown_seconds: 15       # Per rule+track_id cooldown
  daily_cap: 50              # Max alerts per calendar day
  # token and chat_ids loaded from .env, not config.yaml
```

**File:** `.env` (secrets only)

```bash
TELEGRAM_BOT_TOKEN=your_bot_token_here
TELEGRAM_CHAT_IDS=123456789,987654321

# Optional role tokens for Flask server
ADMIN_TOKEN=secure_admin_token
SECURITY_TOKEN=secure_security_token
VIEWER_TOKEN=secure_viewer_token
```

**File:** `.env.example` (template committed to git)
- Contains all required keys with placeholder values
- Users copy to `.env` and fill in real secrets

---

## Dependencies on Other Modules

- **Edge Module** (`src/main.py`): Calls evidence.save_evidence() and alerts.send_photo()
- **Config Loader** (`src/config_loader.py`): Loads settings for all modules
- **Logging** (`src/logging_config.py`): Provides logger instances

**External Dependencies:**
- `requests` - HTTP client for Telegram API
- `python-dotenv` - Load .env files
- `PyYAML` - Parse YAML config
- `Flask` - Web framework (FastAPI planned)

---

## Known Issues & TODOs

### Critical (MVP Blockers)
- ❌ **No evidence encryption at rest** (AES-256 required by spec)
  - Current: Images saved as plaintext JPEG
  - Required: Encrypt before writing to disk, decrypt on read
  - Key management: Environment variable or key file (not in repo)
- ❌ **No pairing service** (mobile app dependency)
  - Need: Code generation, validation, device registration
  - Need: JWT token issuance for paired devices
- ❌ **No proper REST API** (Flask server is placeholder)
  - Need: FastAPI migration with OpenAPI docs
  - Need: Structured routes (/api/evidence, /api/pairing, /api/config)
- ❌ **No authentication/authorization** (env tokens are demo-only)
  - Need: JWT-based auth with role enforcement
  - Need: Manager vs Staff role separation
- ❌ **No push notifications** (Telegram only)
  - Need: Firebase Cloud Messaging (FCM) integration
  - Alternative: Self-hosted ntfy.sh

### High Priority
- ⚠️ **No tamper-evident audit log** (basic logging only)
  - Need: Hash chain (each log entry hashes previous entry)
  - Need: Log evidence views, exports, config changes
- ⚠️ **Retention policy not enforced** (configured but manual)
  - prune_old_evidence() exists but not called automatically
  - Need: Scheduled task or startup check
- ⚠️ **No TLS/HTTPS** (plaintext HTTP)
  - Acceptable for local demo on localhost
  - Required for any network deployment
- ⚠️ **No rate limiting** (vulnerable to abuse)
  - Need: Rate limit on pairing redemption attempts
  - Need: Rate limit on evidence API endpoints

### Medium Priority
- 🔧 **No email fallback alerts** (planned as redundancy)
- 🔧 **No alert batching** (fires immediately on every trigger)
  - Could batch low-priority alerts, send digest every N minutes
  - High-priority alerts should always bypass batching
- 🔧 **Alert cooldown/daily cap in-memory** (resets on restart)
  - Consider: Persistent state in SQLite for long-running deploys
- 🔧 **No health check endpoint** (can't monitor system status)
- 🔧 **No graceful shutdown** (logs "System stop" but doesn't flush buffers)

### Low Priority
- 🔧 **No evidence export (ZIP with manifest)** (manager feature)
- 🔧 **No evidence search/filter API** (timestamp, rule, camera)
- 🔧 **Path traversal vulnerability in /evidence/image** (no sanitization)
- 🔧 **No log rotation** (app.log grows unbounded)
- 🔧 **No metrics/telemetry** (uptime, alert counts, detection counts)

---

## Testing

**Current State:** ❌ No automated tests for backend module

**Required Tests (Not Written Yet):**
- [ ] Evidence save/load roundtrip
- [ ] Evidence encryption/decryption roundtrip (after implementing encryption)
- [ ] SHA-256 integrity verification (verify_evidence logic)
- [ ] Telegram alert dispatch (mock Telegram API)
- [ ] Alert cooldown logic (duplicate suppression)
- [ ] Alert daily cap logic (stops after limit)
- [ ] Pairing code generation (after implementing pairing service)
- [ ] Pairing code redemption (single-use, expiry, rate limiting)
- [ ] JWT token validation (after implementing auth)
- [ ] Role-based access control (manager vs staff permissions)
- [ ] Audit log hash chain verification (after implementing tamper-evident log)

**Integration Tests (Planned Week 9):**
- [ ] End-to-end alert path: rule trigger → evidence saved → alert sent → fallback on failure
- [ ] End-to-end pairing flow: generate code → redeem → device registered → replay rejected

---

## Security Considerations

### Current Security Posture

**✅ Good:**
- Secrets in .env (not committed to git)
- SHA-256 integrity hashing for evidence
- No third-party data sharing (all processing local)
- Telegram chat ID whitelist (only configured IDs receive alerts)

**⚠️ Weak (Acceptable for Local Demo):**
- Role tokens in environment variables (not JWT)
- No TLS (plaintext HTTP on localhost)
- Basic path traversal vulnerability in evidence image serving

**❌ Missing (Required for MVP):**
- Evidence encryption at rest
- JWT authentication with proper expiry/refresh
- Role-based access control enforcement (server-side)
- Tamper-evident audit logging
- Input validation and sanitization
- Rate limiting on sensitive endpoints

### Threat Model

**T1: Physical access to evidence directory**
- Current: Attacker can view all evidence images (plaintext)
- Mitigation: AES-256 encryption (Week 7)

**T2: Stolen device (mobile app)**
- Current: N/A (mobile app not built yet)
- Planned Mitigation: Manager can revoke device token from dashboard

**T3: Insider misuse of evidence**
- Current: No audit trail of who viewed/exported evidence
- Mitigation: Tamper-evident audit log (Week 7)

**T4: Pairing code brute force**
- Current: N/A (pairing not implemented)
- Planned Mitigation: 6-digit code (1M combinations), 10-min expiry, single-use, rate limiting (5 attempts/minute/IP)

**T5: Telegram token leak**
- Current: If .env leaked, attacker could send messages as bot
- Mitigation: .env in .gitignore, file permissions (600 on Linux), consider env encryption for production

**T6: Replay attacks (reuse of pairing code or JWT)**
- Current: N/A
- Planned Mitigation: Single-use pairing codes, JWT expiry + refresh token pattern

---

## Future Enhancements (Post-MVP)

### Week 7: Security Hardening
1. **FastAPI migration** - Modern async framework
2. **JWT authentication** - Industry-standard token-based auth
3. **AES-256 evidence encryption** - Encrypt all snapshots at rest
4. **Tamper-evident audit log** - Hash chain for accountability
5. **TLS/HTTPS** - Self-signed cert for demo, Let's Encrypt for production
6. **Rate limiting** - Protect against brute force and abuse

### Week 6-7: Pairing Service
7. **Pairing code generation** - Manager-initiated, 6-digit numeric
8. **Pairing code validation** - Single-use, 10-min expiry, rate-limited
9. **Device registration** - JWT token issuance for paired devices
10. **Device management API** - List devices, revoke access

### Week 6-7: Alert Channels
11. **Push notifications (FCM)** - Primary channel for mobile app
12. **Email fallback** - Redundancy if push fails
13. **Alert batching** - Digest mode for low-priority alerts

### Post-MVP: Advanced Features
14. **Multi-tenant support** - Multiple stores in single deployment
15. **PostgreSQL migration** - Replace SQLite for production scale
16. **Metrics & monitoring** - Prometheus/Grafana integration
17. **Evidence retention automation** - Scheduled pruning with legal hold flag
18. **Evidence export with manifest** - ZIP download with SHA-256 manifest
19. **Webhook alerts** - Generic HTTP callback for integrations
20. **GraphQL API** - Alternative to REST for flexible queries

---

## API Specification (Planned)

**Current:** Flask server with ad-hoc endpoints  
**Target:** FastAPI with OpenAPI documentation

### Planned Endpoints (Week 7)

**Authentication:**
- `POST /api/auth/login` - Manager login (username/password) → JWT
- `POST /api/auth/refresh` - Refresh expired JWT
- `POST /api/auth/logout` - Invalidate JWT

**Pairing (Week 6-7):**
- `POST /api/pairing/generate` - Manager generates 6-digit code (requires manager JWT)
- `POST /api/pairing/redeem` - Staff redeems code → device JWT
- `GET /api/pairing/devices` - List paired devices (requires manager JWT)
- `DELETE /api/pairing/devices/{id}` - Revoke device access (requires manager JWT)

**Evidence:**
- `GET /api/evidence` - List all evidence (paginated, filterable)
- `GET /api/evidence/{id}` - Get evidence detail + metadata
- `GET /api/evidence/{id}/image` - Download evidence image (decrypted)
- `POST /api/evidence/{id}/resolve` - Mark incident as resolved/false-positive (staff JWT)
- `POST /api/evidence/export` - Export evidence ZIP (manager JWT)

**Configuration (Manager Only):**
- `GET /api/config/rules` - Get current rule thresholds
- `PUT /api/config/rules` - Update rule thresholds
- `GET /api/config/zones` - Get current zone coordinates
- `PUT /api/config/zones` - Update zone coordinates

**System:**
- `GET /api/health` - Health check (no auth)
- `GET /api/metrics` - System metrics (requires auth)

**WebSocket (Week 8):**
- `WS /api/live` - Live camera feed (MJPEG over WebSocket)

---

## Runbook / Operational Notes

### Starting the Flask Server (Current)

```powershell
# Set role tokens (optional, for demo)
$env:ADMIN_TOKEN="your_admin_token"
$env:SECURITY_TOKEN="your_security_token"
$env:VIEWER_TOKEN="your_viewer_token"

# Start server
python -m src.server

# Access at http://localhost:5000
```

### Setting Up Telegram Alerts

1. **Create Telegram Bot:**
   - Message [@BotFather](https://t.me/BotFather) on Telegram
   - Send `/newbot` and follow prompts
   - Copy bot token (format: `1234567890:ABCdefGHI...`)

2. **Get Chat ID:**
   - Start conversation with your new bot (send any message)
   - Visit `https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getUpdates`
   - Find `"chat":{"id":123456789}` in JSON response

3. **Configure:**
   - Add to `.env`:
     ```
     TELEGRAM_BOT_TOKEN=your_bot_token
     TELEGRAM_CHAT_IDS=your_chat_id
     ```
   - Multiple chat IDs: `TELEGRAM_CHAT_IDS=123456789,987654321`

4. **Test:**
   - Run `python src/main.py --source 0`
   - Trigger a rule (e.g., stand in shelf zone for 5+ seconds)
   - Check Telegram for alert photo

### Verifying Evidence Integrity

```powershell
# Check all evidence files
python -m src.verify_evidence --dir evidence

# Output shows PASS/FAIL for each file
# FAIL indicates tampering (hash mismatch)
```

### Pruning Old Evidence

```powershell
# Manual prune (retention_days from config.yaml)
python -c "from src.evidence import prune_old_evidence; from src.logging_config import setup_logging; prune_old_evidence('evidence', 7, setup_logging())"

# TODO: Add CLI tool or scheduled task for automatic pruning
```

### Troubleshooting

**Telegram alerts not sending:**
- Check bot token in .env (no spaces, correct format)
- Check chat IDs (numeric, comma-separated if multiple)
- Check `alerts.enabled: true` in config.yaml
- Check internet connection (Telegram API requires network access)
- Check logs/app.log for error messages

**Evidence not saving:**
- Check `storage.evidence_dir` exists and is writable
- Check disk space (JPEG files are ~50-200KB each)
- Check logs for permission errors

**Flask server won't start:**
- Check port 5000 not already in use (`netstat -an | findstr 5000`)
- Check Python environment activated
- Check Flask installed (`pip list | findstr Flask`)

**"ModuleNotFoundError" errors:**
- Activate virtual environment (`.\.venv\Scripts\Activate.ps1`)
- Install dependencies (`pip install -r requirements.txt`)

---

**Last Updated:** 2026-08-26  
**Next Review:** After implementing evidence encryption and pairing service (Week 6-7)  
**Maintainer:** AutoGuard Development Team
