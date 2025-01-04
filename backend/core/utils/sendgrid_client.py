import os
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail, Email, To, Content, Header
from django.conf import settings

def send_password_reset_email(to_email: str, reset_url: str, ip_address: str = ''):
    print(f"Attempting to send password reset email to {to_email}")
    print(f"Reset URL: {reset_url}")
    
    html_content = f'''
        <div style="font-family: Arial, sans-serif; max-width: 600px; margin: 0 auto;">
            <div style="text-align: center; margin-bottom: 20px;">
                <img src="{settings.FRONTEND_URL}/logo.png" alt="Gift Sync" style="max-width: 150px;">
            </div>

            <h2 style="color: #2c3e50; margin-bottom: 20px;">Password Reset Request</h2>
            
            <p style="color: #34495e; line-height: 1.5;">
                Hello,<br><br>
                You recently requested to reset your password for your Gift Sync account.
            </p>
            
            <p style="color: #34495e; line-height: 1.5;">
                Click the button below to reset your password:
            </p>
            
            <p style="text-align: center; margin: 30px 0;">
                <a href="{reset_url}" 
                   style="background-color: #3498db; 
                          color: white; 
                          padding: 12px 25px; 
                          text-decoration: none; 
                          border-radius: 5px;
                          display: inline-block;">
                    Reset Password
                </a>
            </p>
            
            <p style="color: #34495e; line-height: 1.5;">
                If you didn't request this password reset, you can safely ignore this email.
                The link will expire in 24 hours.
            </p>
            
            <p style="color: #34495e; line-height: 1.5; font-size: 13px;">
                For security, this request was received from IP address {ip_address}.
                If you did not make this request, please contact support immediately.
            </p>
            
            <hr style="border: none; border-top: 1px solid #eee; margin: 30px 0;">
            
            <p style="color: #7f8c8d; font-size: 11px; text-align: center;">
                Best regards,<br>
                The Gift Sync Team<br><br>
                This is an automated message, please do not reply directly to this email.<br>
                If you need assistance, please contact support at crwilson311@gmail.com
            </p>
            
            <p style="color: #95a5a6; font-size: 10px; text-align: center; margin-top: 20px;">
                Gift Sync • Secure Gift Registry<br>
                You're receiving this email because a password reset was requested for your account.<br>
                To unsubscribe from these alerts, please contact support.
            </p>
        </div>
    '''

    # Create the email components
    from_email = Email("crwilson311@gmail.com", "Gift Sync")
    to_email = To(to_email)
    subject = "Reset Your Gift Sync Account Password"
    content = Content("text/html", html_content)

    message = Mail(
        from_email=from_email,
        to_emails=to_email,
        subject=subject,
        html_content=content
    )

    # Add headers to the first personalization
    message.personalizations[0].headers = {
        "List-Unsubscribe": f"<{settings.FRONTEND_URL}/unsubscribe>, <mailto:crwilson311@gmail.com?subject=unsubscribe>",
        "List-Unsubscribe-Post": "List-Unsubscribe=One-Click",
        "X-Entity-Ref-ID": f"password-reset-{to_email}"
    }

    # Add category for tracking
    message.add_category("password-reset")

    try:
        api_key = os.getenv('SENDGRID_API_KEY')
        if not api_key:
            print("SendGrid API key not found!")
            return False

        print(f"Using API key starting with: {api_key[:10]}...")
        sg = SendGridAPIClient(api_key)
        
        # Convert the Mail object to a dict for sending
        email_data = message.get()
        print("Email data:", email_data)
        
        print("Sending email...")
        response = sg.client.mail.send.post(request_body=email_data)
        
        print(f"Response Status Code: {response.status_code}")
        print(f"Response Headers: {response.headers}")
        print(f"Response Body: {response.body}")
        
        if response.status_code == 202:
            print("Email sent successfully!")
            return True
        else:
            print(f"Unexpected status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"SendGrid error: {str(e)}")
        if hasattr(e, 'body'):
            print(f"Error body: {e.body.decode() if isinstance(e.body, bytes) else e.body}")
        if hasattr(e, 'headers'):
            print(f"Error headers: {e.headers}")
        return False 