import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import pandas as pd
from flask import Flask, render_template, request, flash

app = Flask(__name__)
app.secret_key = "supersecretkey"

# SMTP Configuration
SMTP_SERVER = 'smtp.gmail.com'
SMTP_PORT = 587
SENDER_EMAIL = 'csi.srmist@gmail.com'
SENDER_PASSWORD = 'flts aixn xunt sias'  # Use an app-specific password for Gmail

def send_email(recipient_email, subject, body, attachments=None):
    try:
        msg = MIMEMultipart()
        msg['From'] = SENDER_EMAIL
        msg['To'] = recipient_email
        msg['Subject'] = subject

        # Attach body
        msg.attach(MIMEText(body, 'plain'))

        # Attach files
        if attachments:
            for attachment in attachments:
                with open(attachment, 'rb') as file:
                    part = MIMEBase('application', 'octet-stream')
                    part.set_payload(file.read())
                    encoders.encode_base64(part)
                    part.add_header('Content-Disposition', f'attachment; filename={os.path.basename(attachment)}')
                    msg.attach(part)

        # Connect to SMTP server and send email
        with smtplib.SMTP(SMTP_SERVER, SMTP_PORT) as server:
            server.starttls()
            server.login(SENDER_EMAIL, SENDER_PASSWORD)
            server.send_message(msg)
        return True
    except Exception as e:
        print(f"Error: {e}")
        return False

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        # Get form data
        subject = request.form['subject']
        body_template = request.form['body']
        attachment_files = request.files.getlist('attachments')

        # Save attachments
        attachments = []
        for file in attachment_files:
            if file.filename:
                file_path = os.path.join('attachments', file.filename)
                file.save(file_path)
                attachments.append(file_path)

        # Read CSV file
        try:
            df = pd.read_csv('recipients.csv')
            for _, row in df.iterrows():
                body = body_template
                for column in df.columns:
                    placeholder = f"{{{column}}}"  # Format placeholder as {ColumnName}
                    body = body.replace(placeholder, str(row[column]))

                # Send email
                if send_email(row['Email'], subject, body, attachments):
                    flash(f"Email sent to {row['Name']} ({row['Email']})", "success")
                else:
                    flash(f"Failed to send email to {row['Name']} ({row['Email']})", "error")

            # Clean up attachments
            for attachment in attachments:
                os.remove(attachment)
        except Exception as e:
            flash(f"Error: {e}", "error")

    return render_template('index.html')

if __name__ == '__main__':
    if not os.path.exists('attachments'):
        os.makedirs('attachments')
    app.run(debug=True)
