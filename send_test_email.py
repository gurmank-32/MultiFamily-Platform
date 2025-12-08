"""
Script to send a test email with the Dallas Rent Control update
"""
from email_alerts import EmailAlertSystem
from datetime import datetime

def send_test_email():
    """Send test email to safaazam2022@gmail.com"""
    email_system = EmailAlertSystem()
    
    # Create test update data matching the Dallas demo
    update_data = {
        "source_name": "Dallas Rent Control 2025 (DEMO)",
        "url": "test_rent_control_dallas_demo.html",
        "summary": "A newly announced policy in Dallas, Texas claims that landlords are now prohibited from raising rent by more than $250 above the tenant's existing monthly rent. For example, if a tenant currently pays $1,000 per month, the maximum legal rent after an increase would be $1,250. If the rent today is $2,000, the legal maximum would be $2,250. Under this rule, it would not matter whether the unit is remodeled, upgraded, or located in a premium neighborhood — the increase still cannot exceed a $250 gap from the prior lease.",
        "affected_cities": ["Dallas"],
        "category": "Rent Control",
        "detected_at": datetime.now().strftime('%Y-%m-%d')
    }
    
    email = "safaazam2022@gmail.com"
    
    print(f"Sending test email to {email}...")
    result = email_system.send_update_alert(email, update_data)
    
    if result:
        print(f"[SUCCESS] Email sent successfully to {email}")
    else:
        print(f"[INFO] Email saved to file (check emails/ folder)")

if __name__ == "__main__":
    send_test_email()

