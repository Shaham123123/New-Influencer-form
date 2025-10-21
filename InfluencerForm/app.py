from flask import Flask, render_template, request, redirect
import gspread
from oauth2client.service_account import ServiceAccountCredentials
import smtplib
from email.message import EmailMessage
import os
from dotenv import load_dotenv
load_dotenv()

app = Flask(__name__)

# Setup Google Sheets access
print("🔄 Loading Google Sheets credentials...")
scope = ['https://spreadsheets.google.com/feeds', 'https://www.googleapis.com/auth/drive']
creds = ServiceAccountCredentials.from_json_keyfile_name('secrets/credentials.json', scope)
client = gspread.authorize(creds)
sheet = client.open("Influencer Submissions").worksheet("Sheet1")
print("✅ Connected to Google Sheet")

# Function to send confirmation email
def send_confirmation_email(receiver_email, full_name):
    print(f"📤 Preparing to send email to {receiver_email}")
    
    sender_email = os.environ.get("EMAIL_USER")
    app_password = os.environ.get("EMAIL_PASS")

    if not sender_email or not app_password:
        print("❌ Missing EMAIL_USER or EMAIL_PASS in environment variables.")
        return

    subject = "Welcome to Loom Abayas 🌿"
    body = f"""
Ahlan {full_name},

🌸 Thank you for joining Loom Abaya’s Creator Community!

We’re thrilled to have you. Our team will reach out when a collaboration opportunity aligns with your style.

Until then, stay graceful and keep inspiring.

Warm regards,  
Loom Abayas Team
"""

    message = EmailMessage()
    message.set_content(body)
    message["Subject"] = subject
    message["From"] = sender_email
    message["To"] = receiver_email

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
            server.login(sender_email, app_password)
            server.send_message(message)
        print("✅ Email sent successfully to", receiver_email)
    except Exception as e:
        print("❌ Failed to send email:", e)

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        full_name = request.form["full_name"]
        email = request.form["email"]
        print("📥 Form submission received for:", full_name, email)

        data = [
            full_name,
            request.form["country"],
            request.form["state"],
            request.form["city"],
            request.form["abaya_size"],
            request.form.get("custom_size", ""),
            request.form["followers"],
            request.form["reel_views"],
            request.form["instagram_id"],
            email,
            request.form["contact_number"],
            request.form["queries"],
            request.form["days_required"]
        ]

        try:
            sheet.append_row(data)
            print("✅ Data added to Google Sheet.")
        except Exception as e:
            print("❌ Failed to add data to Google Sheet:", e)

        # Send confirmation email
        print("📧 Calling send_confirmation_email()...")
        send_confirmation_email(email, full_name)

        return redirect("/success")
    return render_template("form.html", sizes=[52, 54, 56, 58, 60, "Custom"])

@app.route("/success")
def success():
    return render_template("success.html")

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5001))
    app.run(host="0.0.0.0", port=port)





