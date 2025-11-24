"""
Daily scraper for regulation updates
Runs automatically to check for updates daily
"""
from update_checker import UpdateChecker
from email_alerts import EmailAlertSystem
import schedule
import time
from datetime import datetime

class DailyScraper:
    def __init__(self):
        self.update_checker = UpdateChecker()
        self.email_system = EmailAlertSystem()
    
    def run_daily_check(self):
        """Run daily update check and send alerts"""
        print(f"[{datetime.now()}] Starting daily regulation update check...")
        
        try:
            # Check for updates
            updates = self.update_checker.check_for_updates()
            
            if updates:
                print(f"[{datetime.now()}] Found {len(updates)} new update(s)")
                
                # Send email alerts to subscribers
                for update in updates:
                    notified = self.email_system.notify_subscribers(update)
                    print(f"[{datetime.now()}] Notified {len(notified)} subscribers about: {update['source_name']}")
            else:
                print(f"[{datetime.now()}] No new updates detected")
            
            # Send daily summary reports to all subscribers
            print(f"[{datetime.now()}] Sending daily summary reports...")
            total_summaries = self.email_system.send_daily_summaries_to_all_subscribers()
            print(f"[{datetime.now()}] Sent {total_summaries} daily summary report(s)")
        
        except Exception as e:
            print(f"[{datetime.now()}] Error during daily check: {str(e)}")
    
    def start_scheduler(self):
        """Start the daily scheduler"""
        # Schedule daily check at 9 AM
        schedule.every().day.at("09:00").do(self.run_daily_check)
        
        # Also allow manual trigger
        print("Daily scraper scheduled to run at 9:00 AM every day")
        print("Press Ctrl+C to stop")
        
        # Run scheduler
        while True:
            schedule.run_pending()
            time.sleep(60)  # Check every minute

def run_daily_scraper():
    """Main function to run daily scraper"""
    scraper = DailyScraper()
    scraper.start_scheduler()

if __name__ == "__main__":
    run_daily_scraper()
