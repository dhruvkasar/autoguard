"""
Database module for AutoGuard evidence management
Provides SQLite database operations for storing evidence metadata
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional
from contextlib import contextmanager
import logging

logger = logging.getLogger(__name__)

# Default database path
DB_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'data', 'autoguard.db')

@contextmanager
def get_db_connection(db_path: str = DB_PATH):
    """Context manager for database connections"""
    conn = sqlite3.connect(db_path)
    conn.row_factory = sqlite3.Row  # Access columns by name
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database error: {e}")
        raise
    finally:
        conn.close()


def init_database(db_path: str = DB_PATH):
    """Initialize database schema"""
    # Ensure data directory exists
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    
    with get_db_connection(db_path) as conn:
        cursor = conn.cursor()
        
        # Evidence table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS evidence (
                id TEXT PRIMARY KEY,
                camera_id TEXT NOT NULL,
                timestamp TEXT NOT NULL,
                person_id INTEGER NOT NULL,
                rule TEXT NOT NULL,
                image_path TEXT NOT NULL,
                image_hash TEXT,
                description TEXT,
                priority TEXT DEFAULT 'standard',
                resolved BOOLEAN DEFAULT 0,
                resolved_at TEXT,
                resolved_by TEXT,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Indexes for faster queries
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_timestamp 
            ON evidence(timestamp DESC)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_camera_id 
            ON evidence(camera_id)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_rule 
            ON evidence(rule)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_resolved 
            ON evidence(resolved)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_priority 
            ON evidence(priority)
        ''')
        
        # Devices table for mobile device management
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS devices (
                id TEXT PRIMARY KEY,
                device_name TEXT,
                device_model TEXT,
                device_os TEXT,
                role TEXT NOT NULL,
                paired_at TEXT DEFAULT CURRENT_TIMESTAMP,
                last_seen TEXT,
                last_ip TEXT,
                active BOOLEAN DEFAULT 1,
                revoked BOOLEAN DEFAULT 0,
                revoked_at TEXT,
                revoked_by TEXT,
                auth_token TEXT UNIQUE NOT NULL,
                metadata TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                updated_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Pairing codes table for device pairing
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS pairing_codes (
                code TEXT PRIMARY KEY,
                role TEXT NOT NULL,
                created_by TEXT NOT NULL,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP,
                expires_at TEXT NOT NULL,
                used BOOLEAN DEFAULT 0,
                used_at TEXT,
                used_by_device TEXT,
                FOREIGN KEY (used_by_device) REFERENCES devices(id)
            )
        ''')
        
        # Device activity log
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS device_activity (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                activity_type TEXT NOT NULL,
                timestamp TEXT DEFAULT CURRENT_TIMESTAMP,
                ip_address TEXT,
                metadata TEXT,
                FOREIGN KEY (device_id) REFERENCES devices(id)
            )
        ''')
        
        # Indexes for devices
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_devices_role 
            ON devices(role)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_devices_active 
            ON devices(active, revoked)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_pairing_expires 
            ON pairing_codes(expires_at)
        ''')
        
        cursor.execute('''
            CREATE INDEX IF NOT EXISTS idx_device_activity 
            ON device_activity(device_id, timestamp DESC)
        ''')
        
        logger.info(f"Database initialized at {db_path}")


def insert_evidence(
    evidence_id: str,
    camera_id: str,
    timestamp: str,
    person_id: int,
    rule: str,
    image_path: str,
    image_hash: str = None,
    description: str = None,
    priority: str = 'standard',
    metadata: dict = None,
    db_path: str = DB_PATH
) -> bool:
    """Insert new evidence record"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO evidence (
                    id, camera_id, timestamp, person_id, rule,
                    image_path, image_hash, description, priority, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                evidence_id,
                camera_id,
                timestamp,
                person_id,
                rule,
                image_path,
                image_hash,
                description,
                priority,
                json.dumps(metadata) if metadata else None
            ))
        return True
    except sqlite3.IntegrityError:
        logger.warning(f"Evidence {evidence_id} already exists")
        return False
    except Exception as e:
        logger.error(f"Failed to insert evidence: {e}")
        return False


def get_all_evidence(
    date_range: str = 'all',
    rule_type: str = 'all',
    camera_filter: str = 'all',
    resolved_filter: Optional[bool] = None,
    limit: int = 1000,
    offset: int = 0,
    db_path: str = DB_PATH
) -> List[Dict]:
    """Get evidence with filtering options"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Build query with filters
            query = "SELECT * FROM evidence WHERE 1=1"
            params = []
            
            # Date range filter
            if date_range == 'today':
                query += " AND DATE(timestamp) = DATE('now')"
            elif date_range == 'week':
                query += " AND DATE(timestamp) >= DATE('now', '-7 days')"
            elif date_range == 'month':
                query += " AND DATE(timestamp) >= DATE('now', '-30 days')"
            
            # Rule type filter
            if rule_type != 'all':
                rule_map = {
                    'loitering': 'Loitering',
                    'exit_checkout': 'Exit Without Checkout',
                    'shelf_exit': 'Shelf',
                    'violence': 'violence'
                }
                search_term = rule_map.get(rule_type, rule_type)
                query += " AND rule LIKE ?"
                params.append(f"%{search_term}%")
            
            # Camera filter
            if camera_filter != 'all':
                query += " AND camera_id = ?"
                params.append(camera_filter)
            
            # Resolved filter
            if resolved_filter is not None:
                query += " AND resolved = ?"
                params.append(1 if resolved_filter else 0)
            
            # Order by timestamp descending
            query += " ORDER BY timestamp DESC LIMIT ? OFFSET ?"
            params.extend([limit, offset])
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            # Convert to list of dicts
            evidence_list = []
            for row in rows:
                evidence = dict(row)
                # Parse metadata JSON
                if evidence.get('metadata'):
                    try:
                        evidence['metadata'] = json.loads(evidence['metadata'])
                    except:
                        evidence['metadata'] = {}
                evidence_list.append(evidence)
            
            return evidence_list
    except Exception as e:
        logger.error(f"Failed to get evidence: {e}")
        return []


def get_evidence_by_id(evidence_id: str, db_path: str = DB_PATH) -> Optional[Dict]:
    """Get single evidence by ID"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM evidence WHERE id = ?", (evidence_id,))
            row = cursor.fetchone()
            
            if row:
                evidence = dict(row)
                # Parse metadata JSON
                if evidence.get('metadata'):
                    try:
                        evidence['metadata'] = json.loads(evidence['metadata'])
                    except:
                        evidence['metadata'] = {}
                return evidence
            return None
    except Exception as e:
        logger.error(f"Failed to get evidence by ID: {e}")
        return None


def update_evidence_resolution(
    evidence_id: str,
    resolved: bool,
    resolved_by: str = None,
    db_path: str = DB_PATH
) -> bool:
    """Update evidence resolution status"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            if resolved:
                cursor.execute('''
                    UPDATE evidence 
                    SET resolved = 1, 
                        resolved_at = ?, 
                        resolved_by = ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), resolved_by, evidence_id))
            else:
                cursor.execute('''
                    UPDATE evidence 
                    SET resolved = 0, 
                        resolved_at = NULL, 
                        resolved_by = NULL,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                ''', (evidence_id,))
            
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Failed to update resolution status: {e}")
        return False


def get_evidence_stats(db_path: str = DB_PATH) -> Dict:
    """Get evidence statistics"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Total incidents
            cursor.execute("SELECT COUNT(*) FROM evidence")
            total_incidents = cursor.fetchone()[0]
            
            # High priority
            cursor.execute("SELECT COUNT(*) FROM evidence WHERE priority = 'high'")
            high_priority = cursor.fetchone()[0]
            
            # Standard priority (theft alerts)
            cursor.execute("SELECT COUNT(*) FROM evidence WHERE priority = 'standard'")
            theft_alerts = cursor.fetchone()[0]
            
            # Resolved
            cursor.execute("SELECT COUNT(*) FROM evidence WHERE resolved = 1")
            resolved = cursor.fetchone()[0]
            
            return {
                'total_incidents': total_incidents,
                'high_priority': high_priority,
                'theft_alerts': theft_alerts,
                'resolved': resolved
            }
    except Exception as e:
        logger.error(f"Failed to get statistics: {e}")
        return {
            'total_incidents': 0,
            'high_priority': 0,
            'theft_alerts': 0,
            'resolved': 0
        }


def count_evidence(
    date_range: str = 'all',
    rule_type: str = 'all',
    camera_filter: str = 'all',
    resolved_filter: Optional[bool] = None,
    db_path: str = DB_PATH
) -> int:
    """Count evidence with filters"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Build query with filters
            query = "SELECT COUNT(*) FROM evidence WHERE 1=1"
            params = []
            
            # Date range filter
            if date_range == 'today':
                query += " AND DATE(timestamp) = DATE('now')"
            elif date_range == 'week':
                query += " AND DATE(timestamp) >= DATE('now', '-7 days')"
            elif date_range == 'month':
                query += " AND DATE(timestamp) >= DATE('now', '-30 days')"
            
            # Rule type filter
            if rule_type != 'all':
                rule_map = {
                    'loitering': 'Loitering',
                    'exit_checkout': 'Exit Without Checkout',
                    'shelf_exit': 'Shelf',
                    'violence': 'violence'
                }
                search_term = rule_map.get(rule_type, rule_type)
                query += " AND rule LIKE ?"
                params.append(f"%{search_term}%")
            
            # Camera filter
            if camera_filter != 'all':
                query += " AND camera_id = ?"
                params.append(camera_filter)
            
            # Resolved filter
            if resolved_filter is not None:
                query += " AND resolved = ?"
                params.append(1 if resolved_filter else 0)
            
            cursor.execute(query, params)
            return cursor.fetchone()[0]
    except Exception as e:
        logger.error(f"Failed to count evidence: {e}")
        return 0


def delete_evidence(evidence_id: str, db_path: str = DB_PATH) -> bool:
    """Delete evidence record"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("DELETE FROM evidence WHERE id = ?", (evidence_id,))
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Failed to delete evidence: {e}")
        return False


def generate_pairing_code(
    role: str,
    created_by: str,
    expires_minutes: int = 10,
    db_path: str = DB_PATH
) -> Optional[str]:
    """Generate a new pairing code for device registration"""
    import random
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Generate unique 4-digit code
            max_attempts = 10
            for _ in range(max_attempts):
                code = ''.join([str(random.randint(0, 9)) for _ in range(4)])
                
                # Check if code already exists and hasn't expired
                cursor.execute('''
                    SELECT code FROM pairing_codes 
                    WHERE code = ? AND datetime(expires_at) > datetime('now')
                ''', (code,))
                
                if not cursor.fetchone():
                    # Code is unique, insert it
                    expires_at = datetime.now().replace(microsecond=0)
                    from datetime import timedelta
                    expires_at += timedelta(minutes=expires_minutes)
                    
                    cursor.execute('''
                        INSERT INTO pairing_codes (code, role, created_by, expires_at)
                        VALUES (?, ?, ?, ?)
                    ''', (code, role, created_by, expires_at.strftime("%Y-%m-%d %H:%M:%S")))
                    
                    return code
            
            logger.error("Failed to generate unique pairing code after max attempts")
            return None
    except Exception as e:
        logger.error(f"Failed to generate pairing code: {e}")
        return None


def verify_pairing_code(code: str, db_path: str = DB_PATH) -> Optional[Dict]:
    """Verify if pairing code is valid and not expired"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT code, role, created_by, expires_at, used
                FROM pairing_codes
                WHERE code = ? AND datetime(expires_at) > datetime('now') AND used = 0
            ''', (code,))
            
            row = cursor.fetchone()
            if row:
                return dict(row)
            return None
    except Exception as e:
        logger.error(f"Failed to verify pairing code: {e}")
        return None


def register_device(
    code: str,
    device_id: str,
    device_name: str,
    device_model: str,
    device_os: str,
    auth_token: str,
    ip_address: str = None,
    metadata: dict = None,
    db_path: str = DB_PATH
) -> bool:
    """Register a new device using a pairing code"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Verify pairing code
            pairing_info = verify_pairing_code(code, db_path)
            if not pairing_info:
                logger.warning(f"Invalid or expired pairing code: {code}")
                return False
            
            role = pairing_info['role']
            
            # Mark pairing code as used
            cursor.execute('''
                UPDATE pairing_codes
                SET used = 1, used_at = ?, used_by_device = ?
                WHERE code = ?
            ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), device_id, code))
            
            # Insert device
            cursor.execute('''
                INSERT INTO devices (
                    id, device_name, device_model, device_os, role,
                    auth_token, last_seen, last_ip, metadata
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (
                device_id,
                device_name,
                device_model,
                device_os,
                role,
                auth_token,
                datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ip_address,
                json.dumps(metadata) if metadata else None
            ))
            
            # Log activity
            log_device_activity(device_id, 'registered', ip_address, db_path=db_path)
            
            return True
    except sqlite3.IntegrityError as e:
        logger.warning(f"Device {device_id} already exists or duplicate token: {e}")
        return False
    except Exception as e:
        logger.error(f"Failed to register device: {e}")
        return False


def get_all_devices(
    role_filter: str = 'all',
    active_only: bool = False,
    db_path: str = DB_PATH
) -> List[Dict]:
    """Get all devices with optional filtering"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            query = "SELECT * FROM devices WHERE 1=1"
            params = []
            
            if role_filter != 'all':
                query += " AND role = ?"
                params.append(role_filter)
            
            if active_only:
                query += " AND active = 1 AND revoked = 0"
            
            query += " ORDER BY paired_at DESC"
            
            cursor.execute(query, params)
            rows = cursor.fetchall()
            
            devices = []
            for row in rows:
                device = dict(row)
                if device.get('metadata'):
                    try:
                        device['metadata'] = json.loads(device['metadata'])
                    except:
                        device['metadata'] = {}
                devices.append(device)
            
            return devices
    except Exception as e:
        logger.error(f"Failed to get devices: {e}")
        return []


def get_device_by_id(device_id: str, db_path: str = DB_PATH) -> Optional[Dict]:
    """Get device by ID"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM devices WHERE id = ?", (device_id,))
            row = cursor.fetchone()
            
            if row:
                device = dict(row)
                if device.get('metadata'):
                    try:
                        device['metadata'] = json.loads(device['metadata'])
                    except:
                        device['metadata'] = {}
                return device
            return None
    except Exception as e:
        logger.error(f"Failed to get device by ID: {e}")
        return None


def get_device_by_token(auth_token: str, db_path: str = DB_PATH) -> Optional[Dict]:
    """Get device by auth token"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT * FROM devices 
                WHERE auth_token = ? AND active = 1 AND revoked = 0
            ''', (auth_token,))
            row = cursor.fetchone()
            
            if row:
                device = dict(row)
                if device.get('metadata'):
                    try:
                        device['metadata'] = json.loads(device['metadata'])
                    except:
                        device['metadata'] = {}
                return device
            return None
    except Exception as e:
        logger.error(f"Failed to get device by token: {e}")
        return None


def update_device_last_seen(
    device_id: str,
    ip_address: str = None,
    db_path: str = DB_PATH
) -> bool:
    """Update device last seen timestamp"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE devices
                SET last_seen = ?, last_ip = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), ip_address, device_id))
            
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Failed to update device last seen: {e}")
        return False


def revoke_device(
    device_id: str,
    revoked_by: str,
    db_path: str = DB_PATH
) -> bool:
    """Revoke device access"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                UPDATE devices
                SET revoked = 1, 
                    active = 0,
                    revoked_at = ?,
                    revoked_by = ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            ''', (datetime.now().strftime("%Y-%m-%d %H:%M:%S"), revoked_by, device_id))
            
            # Log activity
            log_device_activity(device_id, 'revoked', metadata={'revoked_by': revoked_by}, db_path=db_path)
            
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Failed to revoke device: {e}")
        return False


def log_device_activity(
    device_id: str,
    activity_type: str,
    ip_address: str = None,
    metadata: dict = None,
    db_path: str = DB_PATH
) -> bool:
    """Log device activity"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                INSERT INTO device_activity (device_id, activity_type, ip_address, metadata)
                VALUES (?, ?, ?, ?)
            ''', (
                device_id,
                activity_type,
                ip_address,
                json.dumps(metadata) if metadata else None
            ))
            return True
    except Exception as e:
        logger.error(f"Failed to log device activity: {e}")
        return False


def get_device_stats(db_path: str = DB_PATH) -> Dict:
    """Get device statistics"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            
            # Total devices
            cursor.execute("SELECT COUNT(*) FROM devices WHERE revoked = 0")
            total = cursor.fetchone()[0]
            
            # Active devices (seen in last 5 minutes)
            cursor.execute('''
                SELECT COUNT(*) FROM devices 
                WHERE revoked = 0 AND active = 1
                AND datetime(last_seen) > datetime('now', '-5 minutes')
            ''')
            active = cursor.fetchone()[0]
            
            # Idle devices (not seen in 5 minutes but not revoked)
            cursor.execute('''
                SELECT COUNT(*) FROM devices 
                WHERE revoked = 0 AND active = 1
                AND (datetime(last_seen) <= datetime('now', '-5 minutes') OR last_seen IS NULL)
            ''')
            idle = cursor.fetchone()[0]
            
            return {
                'total': total,
                'active': active,
                'idle': idle
            }
    except Exception as e:
        logger.error(f"Failed to get device stats: {e}")
        return {'total': 0, 'active': 0, 'idle': 0}


def cleanup_expired_pairing_codes(db_path: str = DB_PATH) -> int:
    """Remove expired pairing codes"""
    try:
        with get_db_connection(db_path) as conn:
            cursor = conn.cursor()
            cursor.execute('''
                DELETE FROM pairing_codes
                WHERE datetime(expires_at) <= datetime('now')
            ''')
            return cursor.rowcount
    except Exception as e:
        logger.error(f"Failed to cleanup pairing codes: {e}")
        return 0


if __name__ == '__main__':
    # Test database initialization
    logging.basicConfig(level=logging.INFO)
    init_database()
    print("Database initialized successfully")
