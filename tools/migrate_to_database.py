"""
Migration script to import existing JSON evidence files into SQLite database
Run this once to migrate from JSON-based storage to database storage
"""

import os
import json
import sys
from pathlib import Path

# Add parent directory to path to import src modules
sys.path.insert(0, str(Path(__file__).parent.parent))

from src.database import init_database, insert_evidence, get_evidence_stats
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


def migrate_json_to_db():
    """Migrate all JSON evidence files to SQLite database"""
    
    # Paths
    project_root = Path(__file__).parent.parent
    evidence_dir = project_root / 'evidence'
    db_path = project_root / 'data' / 'autoguard.db'
    
    logger.info("Starting migration from JSON to SQLite database")
    logger.info(f"Evidence directory: {evidence_dir}")
    logger.info(f"Database path: {db_path}")
    
    # Initialize database
    logger.info("Initializing database schema...")
    init_database(str(db_path))
    
    # Check for JSON files
    if not evidence_dir.exists():
        logger.warning(f"Evidence directory not found: {evidence_dir}")
        return
    
    json_files = list(evidence_dir.glob('*.json'))
    logger.info(f"Found {len(json_files)} JSON evidence files")
    
    if len(json_files) == 0:
        logger.info("No JSON files to migrate")
        return
    
    # Migrate each JSON file
    success_count = 0
    skip_count = 0
    error_count = 0
    
    for json_file in json_files:
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            evidence_id = json_file.stem  # Filename without extension
            
            # Extract data from JSON
            camera_id = data.get('camera_id', 'CAM01')
            timestamp = data.get('timestamp', '')
            person_id = data.get('person_id', 0)
            rule = data.get('rule', '')
            image_path = data.get('image_path', '')
            image_hash = data.get('image_hash', '')
            description = data.get('description', '')
            
            # Determine priority
            priority = 'high' if any(x in rule.lower() for x in ['aggressive', 'violence', 'threat', 'weapon', 'freeze']) else 'standard'
            
            # Additional metadata
            metadata = {
                'zone': data.get('zone', ''),
                'confidence': data.get('confidence', 0.0),
                'bbox': data.get('bbox', [])
            }
            
            # Insert into database
            result = insert_evidence(
                evidence_id=evidence_id,
                camera_id=camera_id,
                timestamp=timestamp,
                person_id=person_id,
                rule=rule,
                image_path=image_path,
                image_hash=image_hash,
                description=description,
                priority=priority,
                metadata=metadata,
                db_path=str(db_path)
            )
            
            if result:
                # Handle resolved status
                if data.get('resolved', False):
                    from src.database import update_evidence_resolution
                    resolved_by = data.get('resolved_by', 'migrated')
                    update_evidence_resolution(
                        evidence_id=evidence_id,
                        resolved=True,
                        resolved_by=resolved_by,
                        db_path=str(db_path)
                    )
                
                success_count += 1
                logger.debug(f"Migrated: {json_file.name}")
            else:
                skip_count += 1
                logger.debug(f"Skipped (already exists): {json_file.name}")
                
        except Exception as e:
            error_count += 1
            logger.error(f"Error migrating {json_file.name}: {e}")
    
    # Print summary
    logger.info("\n" + "="*60)
    logger.info("MIGRATION SUMMARY")
    logger.info("="*60)
    logger.info(f"Total JSON files found: {len(json_files)}")
    logger.info(f"Successfully migrated: {success_count}")
    logger.info(f"Skipped (duplicates): {skip_count}")
    logger.info(f"Errors: {error_count}")
    
    # Show database stats
    stats = get_evidence_stats(str(db_path))
    logger.info("\nDatabase Statistics:")
    logger.info(f"  Total incidents: {stats['total_incidents']}")
    logger.info(f"  High priority: {stats['high_priority']}")
    logger.info(f"  Theft alerts: {stats['theft_alerts']}")
    logger.info(f"  Resolved: {stats['resolved']}")
    logger.info("="*60)
    
    if success_count > 0:
        logger.info("\n✅ Migration completed successfully!")
        logger.info(f"Database location: {db_path}")
    else:
        logger.warning("\n⚠️ No new records were migrated")


def backup_json_files():
    """Create backup of JSON evidence files"""
    project_root = Path(__file__).parent.parent
    evidence_dir = project_root / 'evidence'
    backup_dir = evidence_dir / 'json_backup'
    
    if not evidence_dir.exists():
        logger.warning("Evidence directory not found")
        return
    
    json_files = list(evidence_dir.glob('*.json'))
    
    if len(json_files) == 0:
        logger.info("No JSON files to backup")
        return
    
    logger.info(f"Creating backup of {len(json_files)} JSON files...")
    backup_dir.mkdir(exist_ok=True)
    
    for json_file in json_files:
        try:
            backup_file = backup_dir / json_file.name
            backup_file.write_text(json_file.read_text(encoding='utf-8'), encoding='utf-8')
        except Exception as e:
            logger.error(f"Error backing up {json_file.name}: {e}")
    
    logger.info(f"✅ Backup created at: {backup_dir}")


if __name__ == '__main__':
    print("\n" + "="*60)
    print("AutoGuard - JSON to SQLite Migration Tool")
    print("="*60 + "\n")
    
    # Ask for confirmation
    response = input("This will migrate all JSON evidence files to SQLite database.\nContinue? (yes/no): ")
    
    if response.lower() in ['yes', 'y']:
        # Create backup first
        backup_json_files()
        
        # Run migration
        migrate_json_to_db()
        
        print("\n✅ Migration complete!")
        print("\nNext steps:")
        print("1. Verify database contents")
        print("2. Update .env to set USE_DATABASE=true")
        print("3. Test the application")
        print("4. JSON backups are saved in evidence/json_backup/")
    else:
        print("Migration cancelled")
