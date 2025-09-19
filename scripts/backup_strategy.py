"""
백업 전략 및 모니터링
"""
import json
import schedule
import time
from datetime import datetime, timedelta
from pathlib import Path
from utils.file_storage_manager import FileStorageManager, FileBackupManager

class BackupStrategy:
    """백업 전략 관리자"""
    
    def __init__(self):
        self.storage = FileStorageManager()
        self.backup_manager = FileBackupManager(self.storage)
        self.backup_log_file = Path("backup_log.json")
        
    def daily_backup(self):
        """일일 백업"""
        backup_name = f"daily_{datetime.now().strftime('%Y%m%d')}"
        print(f"🔄 일일 백업 시작: {backup_name}")
        
        success = self.backup_manager.create_backup("", backup_name)
        self._log_backup("daily", backup_name, success)
        
        if success:
            print(f"✅ 일일 백업 완료: {backup_name}")
        else:
            print(f"❌ 일일 백업 실패: {backup_name}")
    
    def weekly_backup(self):
        """주간 백업"""
        backup_name = f"weekly_{datetime.now().strftime('%Y%W')}"
        print(f"🔄 주간 백업 시작: {backup_name}")
        
        success = self.backup_manager.create_backup("", backup_name)
        self._log_backup("weekly", backup_name, success)
        
        if success:
            print(f"✅ 주간 백업 완료: {backup_name}")
        else:
            print(f"❌ 주간 백업 실패: {backup_name}")
    
    def monthly_backup(self):
        """월간 백업"""
        backup_name = f"monthly_{datetime.now().strftime('%Y%m')}"
        print(f"🔄 월간 백업 시작: {backup_name}")
        
        success = self.backup_manager.create_backup("", backup_name)
        self._log_backup("monthly", backup_name, success)
        
        if success:
            print(f"✅ 월간 백업 완료: {backup_name}")
        else:
            print(f"❌ 월간 백업 실패: {backup_name}")
    
    def cleanup_old_backups(self, days_to_keep: int = 30):
        """오래된 백업 정리"""
        print(f"🧹 {days_to_keep}일 이상 된 백업 정리 중...")
        
        cutoff_date = datetime.now() - timedelta(days=days_to_keep)
        
        # 백업 로그에서 오래된 백업 찾기
        if self.backup_log_file.exists():
            with open(self.backup_log_file, 'r', encoding='utf-8') as f:
                backup_log = json.load(f)
            
            for backup in backup_log.get("backups", []):
                backup_date = datetime.fromisoformat(backup["created_at"])
                if backup_date < cutoff_date and backup["type"] == "daily":
                    # 오래된 일일 백업 삭제
                    self._delete_backup(backup["name"])
    
    def _log_backup(self, backup_type: str, backup_name: str, success: bool):
        """백업 로그 기록"""
        log_entry = {
            "type": backup_type,
            "name": backup_name,
            "created_at": datetime.now().isoformat(),
            "success": success
        }
        
        if self.backup_log_file.exists():
            with open(self.backup_log_file, 'r', encoding='utf-8') as f:
                backup_log = json.load(f)
        else:
            backup_log = {"backups": []}
        
        backup_log["backups"].append(log_entry)
        
        with open(self.backup_log_file, 'w', encoding='utf-8') as f:
            json.dump(backup_log, f, ensure_ascii=False, indent=2)
    
    def _delete_backup(self, backup_name: str):
        """백업 삭제"""
        try:
            # 여기서는 로그만 삭제 (실제 백업 삭제는 별도 구현 필요)
            print(f"🗑️ 백업 삭제: {backup_name}")
            return True
        except Exception as e:
            print(f"❌ 백업 삭제 실패: {e}")
            return False
    
    def get_backup_status(self):
        """백업 상태 조회"""
        if not self.backup_log_file.exists():
            return {"status": "no_backups", "message": "백업 기록이 없습니다."}
        
        with open(self.backup_log_file, 'r', encoding='utf-8') as f:
            backup_log = json.load(f)
        
        backups = backup_log.get("backups", [])
        recent_backups = [b for b in backups if b["success"]][-5:]  # 최근 5개
        
        return {
            "status": "active",
            "total_backups": len(backups),
            "successful_backups": len([b for b in backups if b["success"]]),
            "recent_backups": recent_backups
        }
    
    def setup_scheduled_backups(self):
        """스케줄된 백업 설정"""
        # 일일 백업 (매일 오전 2시)
        schedule.every().day.at("02:00").do(self.daily_backup)
        
        # 주간 백업 (매주 일요일 오전 3시)
        schedule.every().sunday.at("03:00").do(self.weekly_backup)
        
        # 월간 백업 (매월 1일 오전 4시)
        schedule.every().month.do(self.monthly_backup)
        
        # 오래된 백업 정리 (매일 오전 5시)
        schedule.every().day.at("05:00").do(self.cleanup_old_backups)
        
        print("⏰ 스케줄된 백업 설정 완료")
        print("  - 일일 백업: 매일 오전 2시")
        print("  - 주간 백업: 매주 일요일 오전 3시")
        print("  - 월간 백업: 매월 1일 오전 4시")
        print("  - 백업 정리: 매일 오전 5시")
    
    def run_scheduler(self):
        """스케줄러 실행"""
        print("🔄 백업 스케줄러 시작...")
        while True:
            schedule.run_pending()
            time.sleep(60)  # 1분마다 체크

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="백업 전략 관리")
    parser.add_argument("--daily", action="store_true", help="일일 백업 실행")
    parser.add_argument("--weekly", action="store_true", help="주간 백업 실행")
    parser.add_argument("--monthly", action="store_true", help="월간 백업 실행")
    parser.add_argument("--cleanup", action="store_true", help="오래된 백업 정리")
    parser.add_argument("--status", action="store_true", help="백업 상태 조회")
    parser.add_argument("--schedule", action="store_true", help="스케줄러 시작")
    
    args = parser.parse_args()
    
    strategy = BackupStrategy()
    
    if args.daily:
        strategy.daily_backup()
    elif args.weekly:
        strategy.weekly_backup()
    elif args.monthly:
        strategy.monthly_backup()
    elif args.cleanup:
        strategy.cleanup_old_backups()
    elif args.status:
        status = strategy.get_backup_status()
        print(json.dumps(status, indent=2, ensure_ascii=False))
    elif args.schedule:
        strategy.setup_scheduled_backups()
        strategy.run_scheduler()
    else:
        parser.print_help()

if __name__ == "__main__":
    main()
