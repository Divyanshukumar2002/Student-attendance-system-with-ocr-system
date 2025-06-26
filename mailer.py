from flask_mail import Message
from extensions import mail  
def send_credentials(to_email, username, password):
    login_url = "http://localhost:5000/auth/login" 

    msg = Message(
        subject="Your Login Credentials",
        sender="your_email@gmail.com",
        recipients=[to_email]
    )
    msg.body = f"""Hello {username},

        Your login credentials:
        Username: {username}
        Password: {password}
        
        Please change your password on first login.
        
        Login here: {login_url}
        """

    mail.send(msg)