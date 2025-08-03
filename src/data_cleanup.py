"""
Data Cleanup Module
Automatically removes old scraped data files to prevent storage bloat.
"""

import os
import time
import threading
import logging
from datetime import datetime, timedelta
from pathlib import Path

logger = logging.getLogger(__name__)

class DataCleanup:
    """Handles automatic cleanup of old data files."""
    
    def __init__(self, data_dir: str = "data", max_age_hours: int = 1):
        self.data_dir = Path(data_dir)
        self.max_age_hours = max_age_hours
        self.cleanup_thread = None
        self.running = False
        
    def start_cleanup_scheduler(self):
        """Start the background cleanup scheduler."""
        if self.cleanup_thread and self.cleanup_thread.is_alive():
            logger.info("Cleanup scheduler already running")
            return
            
        self.running = True
        self.cleanup_thread = threading.Thread(target=self._cleanup_loop, daemon=True)
        self.cleanup_thread.start()
        logger.info(f"✅ Data cleanup scheduler started (removes files older than {self.max_age_hours}h)")
    
    def stop_cleanup_scheduler(self):
        """Stop the background cleanup scheduler."""
        self.running = False
        if self.cleanup_thread:
            self.cleanup_thread.join(timeout=5)
        logger.info("❌ Data cleanup scheduler stopped")
    
    def _cleanup_loop(self):
        """Background loop that runs cleanup every 10 minutes."""
        while self.running:
            try:
                self.cleanup_old_files()
                # Sleep for 10 minutes between cleanup runs
                for _ in range(600):  # 600 seconds = 10 minutes
                    if not self.running:
                        break
                    time.sleep(1)
            except Exception as e:
                logger.error(f"Error in cleanup loop: {e}")
                time.sleep(60)  # Wait 1 minute on error
    
    def cleanup_old_files(self):
        """Remove files older than max_age_hours."""
        if not self.data_dir.exists():
            return
            
        cutoff_time = datetime.now() - timedelta(hours=self.max_age_hours)
        removed_count = 0
        total_size = 0
        
        try:
            for file_path in self.data_dir.iterdir():
                if file_path.is_file():
                    # Get file modification time
                    file_mtime = datetime.fromtimestamp(file_path.stat().st_mtime)
                    
                    if file_mtime < cutoff_time:
                        # File is older than cutoff time
                        file_size = file_path.stat().st_size
                        total_size += file_size
                        
                        try:
                            file_path.unlink()  # Delete the file
                            removed_count += 1
                            logger.info(f"🗑️ Removed old file: {file_path.name} ({file_size} bytes)")
                        except Exception as e:
                            logger.error(f"Failed to remove file {file_path.name}: {e}")
            
            if removed_count > 0:
                logger.info(f"✅ Cleanup complete: {removed_count} files removed, {total_size} bytes freed")
            else:
                logger.debug("No old files to remove")
                
        except Exception as e:
            logger.error(f"Error during cleanup: {e}")
    
    def get_data_directory_info(self) -> dict:
        """Get information about the data directory."""
        if not self.data_dir.exists():
            return {
                "exists": False,
                "file_count": 0,
                "total_size": 0,
                "files": []
            }
        
        files = []
        total_size = 0
        
        try:
            for file_path in self.data_dir.iterdir():
                if file_path.is_file():
                    stat = file_path.stat()
                    file_info = {
                        "name": file_path.name,
                        "size": stat.st_size,
                        "modified": datetime.fromtimestamp(stat.st_mtime),
                        "age_hours": (datetime.now() - datetime.fromtimestamp(stat.st_mtime)).total_seconds() / 3600
                    }
                    files.append(file_info)
                    total_size += stat.st_size
            
            # Sort by modification time (newest first)
            files.sort(key=lambda x: x["modified"], reverse=True)
            
        except Exception as e:
            logger.error(f"Error getting directory info: {e}")
        
        return {
            "exists": True,
            "file_count": len(files),
            "total_size": total_size,
            "files": files
        }

# Global cleanup instance
_cleanup_instance = None

def get_cleanup_instance() -> DataCleanup:
    """Get the global cleanup instance."""
    global _cleanup_instance
    if _cleanup_instance is None:
        _cleanup_instance = DataCleanup()
    return _cleanup_instance

def start_data_cleanup():
    """Start the global data cleanup scheduler."""
    cleanup = get_cleanup_instance()
    cleanup.start_cleanup_scheduler()

def stop_data_cleanup():
    """Stop the global data cleanup scheduler."""
    cleanup = get_cleanup_instance()
    cleanup.stop_cleanup_scheduler()

def manual_cleanup():
    """Perform manual cleanup of old files."""
    cleanup = get_cleanup_instance()
    cleanup.cleanup_old_files()

def get_data_info() -> dict:
    """Get information about the data directory."""
    cleanup = get_cleanup_instance()
    return cleanup.get_data_directory_info()

# Auto-start cleanup when module is imported (for production)
if __name__ != "__main__":
    try:
        start_data_cleanup()
    except Exception as e:
        logger.error(f"Failed to auto-start data cleanup: {e}")

if __name__ == "__main__":
    # Test the cleanup functionality
    logging.basicConfig(level=logging.INFO)
    cleanup = DataCleanup()
    
    print("Testing data cleanup...")
    cleanup.cleanup_old_files()
    
    info = cleanup.get_data_directory_info()
    print(f"Data directory info: {info}")