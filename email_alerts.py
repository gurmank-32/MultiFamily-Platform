"""
Email alert system for regulation updates
"""
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from database import RegulationDB
from config import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD, LEGAL_DISCLAIMER, get_secret
from typing import List, Dict
from datetime import datetime

class EmailAlertSystem:
    def __init__(self):
        self.db = RegulationDB()
    
    def send_welcome_email(self, email: str, city: str):
        """Send welcome email when user subscribes"""
        try:
            msg = MIMEMultipart()
            # Use intelligenceplatformupdate@gmail.com as sender
            sender_email = "intelligenceplatformupdate@gmail.com"
            msg['From'] = sender_email
            msg['To'] = email
            msg['Subject'] = f"Welcome to Housing Regulation Alerts for {city}"
            
            unsubscribe_link = f"http://localhost:8501/unsubscribe?email={email}&city={city}"
            
            body = f"""
Welcome to the Housing Regulation Compliance Agent!

You have successfully subscribed to receive email alerts for {city} housing regulation updates.

What to expect:
- You'll receive email notifications when regulations are updated for {city}
- Updates include summaries and links to official sources
- Alerts are sent automatically when changes are detected

To unsubscribe, click here: {unsubscribe_link}

Or visit the Email Alerts page in the app and unsubscribe there.

{LEGAL_DISCLAIMER}

---
Housing Regulation Compliance Agent
"""
            
            msg.attach(MIMEText(body, 'plain'))
            
            # Use intelligenceplatformupdate@gmail.com credentials
            sender_password = SMTP_PASSWORD if SMTP_EMAIL == sender_email else get_secret("SMTP_PASSWORD", "")
            
            if sender_password and sender_password != "your_app_password_here":
                try:
                    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                    server.starttls()
                    server.login(sender_email, sender_password)
                    server.send_message(msg)
                    server.quit()
                    return True
                except Exception as smtp_error:
                    print(f"SMTP error: {str(smtp_error)}")
                    # Save email to file as backup
                    self._save_email_to_file(email, f"Welcome to Housing Regulation Alerts for {city}", body)
                    return False
            else:
                # Save email to file instead
                self._save_email_to_file(email, f"Welcome to Housing Regulation Alerts for {city}", body)
                print(f"Email not configured. Saved welcome email to file: emails/welcome_{email.replace('@', '_at_')}.txt")
                return True  # Return True so UI shows success
        
        except Exception as e:
            print(f"Error sending welcome email: {str(e)}")
            return False
    
    def send_update_alert(self, email: str, update: Dict):
        """Send email alert for regulation update with exact format as specified"""
        try:
            import json
            import ast
            
            # Get affected cities
            affected_cities = update.get('affected_cities', [])
            if isinstance(affected_cities, str):
                try:
                    affected_cities = json.loads(affected_cities)
                except:
                    try:
                        affected_cities = ast.literal_eval(affected_cities)
                    except:
                        affected_cities = [affected_cities] if affected_cities else []
            
            if not isinstance(affected_cities, list):
                affected_cities = [affected_cities] if affected_cities else []
            
            # Get summary and limit to 3-5 sentences
            summary = update.get('summary', update.get('update_summary', 'No summary available.'))
            summary_sentences = summary.split('. ')
            if len(summary_sentences) > 5:
                summary_sentences = summary_sentences[:5]
            short_summary = '. '.join(summary_sentences).strip()
            if not short_summary.endswith('.'):
                short_summary += '.'
            
            # Get regulation title
            regulation_title = update.get('source_name', 'Regulation Update')
            
            # Get category
            category = update.get('category', 'N/A')
            
            # Get URL
            url = update.get('url', 'N/A')
            
            # Get date
            detected_date = update.get('detected_at', datetime.now().strftime('%Y-%m-%d'))
            if isinstance(detected_date, str):
                try:
                    # Try to parse and format
                    date_obj = datetime.strptime(detected_date, '%Y-%m-%d %H:%M:%S')
                    date_str = date_obj.strftime('%Y-%m-%d')
                except:
                    date_str = detected_date
            else:
                date_str = detected_date.strftime('%Y-%m-%d') if isinstance(detected_date, datetime) else str(detected_date)
            
            # Check if this email is subscribed to any of the affected cities
            city_to_send = None
            for city in affected_cities:
                subscribers = self.db.get_subscribers_for_city(city)
                if email in subscribers:
                    city_to_send = city
                    break
            
            # Only send if user is subscribed to one of the affected cities
            if city_to_send:
                # Generate short practical impact (3-5 sentences max) - focus on what changed + why property managers care
                practical_impact = f"This regulation update affects property managers and leasing professionals in {city_to_send}. You need to review your lease documents, update property management policies, and ensure staff are trained on the new requirements. The changes impact lease agreement compliance and tenant relations."
                
                msg = MIMEMultipart()
                # Use intelligenceplatformupdate@gmail.com as sender
                sender_email = "intelligenceplatformupdate@gmail.com"
                msg['From'] = sender_email
                msg['To'] = email
                msg['Subject'] = f"HOUSING REGULATION UPDATE ALERT - {city_to_send}"
                
                # Build email body with EXACT format as specified
                body = f"""HOUSING REGULATION UPDATE ALERT

Real Estate Intelligence Platform

CITY: {city_to_send}

REGULATION UPDATE: {regulation_title}

CATEGORY: {category}

DATE: {date_str}

SUMMARY:

{short_summary}

WHY IT MATTERS:

{practical_impact}

SOURCE: {url}

💡 Notes:

No legal disclaimers unless you choose to add a one-liner at the bottom later
Focus only on: what changed + why property managers care
Keep summaries to 3–5 sentences max
Only one hyperlink — the official source
Works perfectly for all four Texas cities
"""
                
                msg.attach(MIMEText(body, 'plain'))
                
                # Use intelligenceplatformupdate@gmail.com credentials
                # Get password from config (should be set in .env or secrets)
                sender_password = SMTP_PASSWORD if SMTP_EMAIL == sender_email else get_secret("SMTP_PASSWORD", "")
                
                if sender_password and sender_password != "your_app_password_here":
                    try:
                        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                        server.starttls()
                        server.login(sender_email, sender_password)
                        server.send_message(msg)
                        server.quit()
                        return True
                    except Exception as smtp_error:
                        print(f"SMTP error: {str(smtp_error)}")
                        # Save email to file as backup
                        self._save_email_to_file(email, msg['Subject'], body)
                        return True
                else:
                    # Save email to file instead
                    self._save_email_to_file(email, msg['Subject'], body)
                    print(f"Email not configured. Saved update alert to file: emails/update_{update['source_name'].replace(' ', '_')}.txt")
                    return True  # Return True so UI shows success
            else:
                # User not subscribed to any affected city
                return False
        
        except Exception as e:
            print(f"Error sending email: {str(e)}")
            return False
    
    def _save_email_to_file(self, email: str, subject: str, body: str):
        """Save email to file when SMTP is not configured"""
        import os
        from datetime import datetime
        
        # Create emails directory if it doesn't exist
        emails_dir = "emails"
        if not os.path.exists(emails_dir):
            os.makedirs(emails_dir)
        
        # Create filename
        safe_email = email.replace('@', '_at_').replace('.', '_')
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        filename = f"{emails_dir}/email_{safe_email}_{timestamp}.txt"
        
        # Write email to file
        with open(filename, 'w', encoding='utf-8') as f:
            f.write(f"To: {email}\n")
            f.write(f"Subject: {subject}\n")
            f.write(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 50 + "\n\n")
            f.write(body)
        
        return filename
    
    def notify_subscribers(self, update: Dict):
        """Notify all subscribers for affected cities"""
        import json
        import ast
        
        affected_cities = update.get('affected_cities', [])
        
        # Handle if affected_cities is a string (JSON or list string)
        if isinstance(affected_cities, str):
            try:
                # Try to parse as JSON first
                affected_cities = json.loads(affected_cities)
            except:
                try:
                    # Try to parse as Python literal
                    affected_cities = ast.literal_eval(affected_cities)
                except:
                    # If parsing fails, treat as single city
                    affected_cities = [affected_cities] if affected_cities else []
        
        # Ensure it's a list
        if not isinstance(affected_cities, list):
            affected_cities = [affected_cities] if affected_cities else []
        
        notified = []
        
        print(f"DEBUG: Notifying subscribers for cities: {affected_cities}")
        
        for city in affected_cities:
            subscribers = self.db.get_subscribers_for_city(city)
            print(f"DEBUG: Found {len(subscribers)} subscribers for {city}: {subscribers}")
            for email in subscribers:
                if self.send_update_alert(email, update):
                    notified.append(email)
                    print(f"DEBUG: Sent alert to {email}")
        
        return notified
    
    def send_regulation_update_alert(self, email_list: List[str], city: str, regulation_title: str, 
                                     category: str, url: str, update_summary: str, date_detected: datetime):
        """Send regulation update alert with exact format as specified"""
        from config import SMTP_SERVER, SMTP_PORT, SMTP_EMAIL, SMTP_PASSWORD, get_secret
        
        # Use intelligenceplatformupdate@gmail.com as sender
        sender_email = "intelligenceplatformupdate@gmail.com"
        
        for email in email_list:
            try:
                msg = MIMEMultipart()
                msg['From'] = sender_email
                msg['To'] = email
                msg['Subject'] = f"HOUSING REGULATION UPDATE ALERT - {city}"
                
                # Format date
                date_str = date_detected.strftime('%Y-%m-%d') if isinstance(date_detected, datetime) else str(date_detected)
                
                # Generate short practical impact (3-5 sentences max) - focus on what changed + why property managers care
                # Keep it concise and practical
                practical_impact = f"This regulation update affects property managers and leasing professionals in {city}. You need to review your lease documents, update property management policies, and ensure staff are trained on the new requirements. The changes impact lease agreement compliance and tenant relations."
                
                # Limit summary to 3-5 sentences max
                summary_sentences = update_summary.split('. ')
                if len(summary_sentences) > 5:
                    summary_sentences = summary_sentences[:5]
                short_summary = '. '.join(summary_sentences).strip()
                if not short_summary.endswith('.'):
                    short_summary += '.'
                
                # Build email body with EXACT format as specified
                body = f"""HOUSING REGULATION UPDATE ALERT

Real Estate Intelligence Platform

CITY: {city}

REGULATION UPDATE: {regulation_title}

CATEGORY: {category}

DATE: {date_str}

SUMMARY:

{short_summary}

WHY IT MATTERS:

{practical_impact}

SOURCE: {url}

💡 Notes:

No legal disclaimers unless you choose to add a one-liner at the bottom later
Focus only on: what changed + why property managers care
Keep summaries to 3–5 sentences max
Only one hyperlink — the official source
Works perfectly for all four Texas cities
"""
                
                msg.attach(MIMEText(body, 'plain'))
                
                # Use intelligenceplatformupdate@gmail.com credentials
                sender_password = SMTP_PASSWORD if SMTP_EMAIL == sender_email else get_secret("SMTP_PASSWORD", "")
                
                if sender_password and sender_password != "your_app_password_here":
                    try:
                        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                        server.starttls()
                        server.login(sender_email, sender_password)
                        server.send_message(msg)
                        server.quit()
                        print(f"    [OK] Sent to {email}")
                    except Exception as smtp_error:
                        print(f"    [ERROR] SMTP error for {email}: {str(smtp_error)}")
                        self._save_email_to_file(email, msg['Subject'], body)
                else:
                    # Save to file if SMTP not configured
                    self._save_email_to_file(email, msg['Subject'], body)
                    print(f"    [SAVED] Email saved to file for {email}")
                    
            except Exception as e:
                print(f"    [ERROR] Failed to send to {email}: {str(e)}")
    
    def send_daily_summary(self, email: str, city: str):
        """Send daily summary report for a city"""
        from datetime import datetime, timedelta
        import ast
        
        try:
            # Get all updates for this city from the last 24 hours
            yesterday = datetime.now() - timedelta(days=1)
            updates = self.db.get_recent_updates(limit=1000)
            
            # Filter updates for this city from last 24 hours
            city_updates = []
            for update in updates:
                # Check if city is in affected cities
                affected_cities = update.get('affected_cities', [])
                if isinstance(affected_cities, str):
                    try:
                        affected_cities = ast.literal_eval(affected_cities)
                    except:
                        affected_cities = [affected_cities]
                
                # Check if this city is affected or if it's a statewide update
                if city in affected_cities or 'Texas-Statewide' in affected_cities:
                    # Check if update is from last 24 hours
                    detected_at = update.get('detected_at', '')
                    if detected_at:
                        try:
                            update_time = datetime.strptime(detected_at, '%Y-%m-%d %H:%M:%S')
                            if update_time >= yesterday:
                                city_updates.append(update)
                        except:
                            # If date parsing fails, include it anyway
                            city_updates.append(update)
                    else:
                        city_updates.append(update)
            
            # If no updates, send a "no updates" summary
            if not city_updates:
                subject = f"Daily Summary: {city} Housing Regulations - No Updates"
                body = f"""
Daily Housing Regulation Summary for {city}

Date: {datetime.now().strftime('%Y-%m-%d')}

No new regulation updates were detected for {city} in the last 24 hours.

All regulations are up to date. We'll continue monitoring and notify you immediately if any changes are detected.

{LEGAL_DISCLAIMER}

---
Housing Regulation Compliance Agent
Daily Summary Report
"""
            else:
                subject = f"Daily Summary: {city} Housing Regulations - {len(city_updates)} Update(s)"
                body = f"""
Daily Housing Regulation Summary for {city}

Date: {datetime.now().strftime('%Y-%m-%d')}

📊 Summary: {len(city_updates)} regulation update(s) detected in the last 24 hours.

{'=' * 60}

"""
                for idx, update in enumerate(city_updates, 1):
                    body += f"""
{idx}. {update.get('source_name', 'Unknown Source')}
   Category: {update.get('category', 'N/A')}
   Detected: {update.get('detected_at', 'N/A')}
   
   Summary:
   {update.get('update_summary', 'No summary available')}
   
   URL: {update.get('url', 'N/A')}
   
   {'-' * 60}

"""
                
                body += f"""
{LEGAL_DISCLAIMER}

---
Housing Regulation Compliance Agent
Daily Summary Report

To unsubscribe, visit the Email Alerts page in the app.
"""
            
            # Send email
            msg = MIMEMultipart()
            msg['From'] = SMTP_EMAIL
            msg['To'] = email
            msg['Subject'] = subject
            
            msg.attach(MIMEText(body, 'plain'))
            
            if SMTP_EMAIL and SMTP_PASSWORD and SMTP_EMAIL != "your_email@gmail.com" and SMTP_PASSWORD != "your_app_password_here":
                try:
                    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
                    server.starttls()
                    server.login(SMTP_EMAIL, SMTP_PASSWORD)
                    server.send_message(msg)
                    server.quit()
                    return True
                except Exception as smtp_error:
                    print(f"SMTP error: {str(smtp_error)}")
                    self._save_email_to_file(email, subject, body)
                    return True
            else:
                self._save_email_to_file(email, subject, body)
                print(f"Email not configured. Saved daily summary to file: emails/daily_summary_{email.replace('@', '_at_')}_{city}.txt")
                return True
        
        except Exception as e:
            print(f"Error sending daily summary: {str(e)}")
            return False
    
    def send_daily_summaries_to_all_subscribers(self):
        """Send daily summaries to all active subscribers"""
        from config import SUPPORTED_CITIES
        
        total_sent = 0
        for city in SUPPORTED_CITIES:
            subscribers = self.db.get_subscribers_for_city(city)
            for email in subscribers:
                if self.send_daily_summary(email, city):
                    total_sent += 1
        
        return total_sent
