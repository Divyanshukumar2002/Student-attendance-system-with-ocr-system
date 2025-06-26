from flask import Blueprint, render_template, request, redirect, url_for, session, flash, current_app
from werkzeug.security import generate_password_hash, check_password_hash
from flask_mail import Message
import uuid
import random, string



from utiles import mailer
from extensions import mail  # Assuming you created a mail instance in a separate extensions file
# from extensions import mongo 


auth = Blueprint("auth", __name__)

@auth.route('/register', methods=["GET", "POST"])
def register():
    from models.database import mongo

    if request.method == "POST":
        role = request.form["role"]
        email = request.form["email"]
        username = request.form["username"]

        # Check if user already exists
        existing_user = mongo.db.students.find_one({"email": email})
        if existing_user:
            flash("Email is already registered.", "warning")
            return redirect(url_for("auth.register"))

        # Generate temp password
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        hashed_password = generate_password_hash(temp_password)

        # Store user in DB
        user_data = {
            "email": email,
            "username": username,
            "password": hashed_password,
            "role": role,
            "first_login": True,
            "must_change_password": True
        }
        mongo.db.students.insert_one(user_data)

        # Send email
        try:
            mailer.send_credentials(email, username, temp_password)
            flash(f"{role.capitalize()} registered successfully. Credentials sent to {email}.", "success")
        except Exception as e:
            print(f"Failed to send email: {e}")
            flash("User created, but email could not be sent.", "danger")

        # Redirect user to login page after registration
        return redirect(url_for("auth.login"))

    return render_template("register.html")



@auth.route('/staff/register', methods=["GET", "POST"])
def staff_register():
    from models.database import mongo

    if request.method == "POST":
        name = request.form["name"]
        email = request.form["email"]
        phone = request.form["phone"]
        department = request.form["department"]
        designation = request.form["designation"]
        role = request.form["role"]  

        # Check if already exists
        existing_staff = mongo.db.staff.find_one({"email": email})
        if existing_staff:
            flash("Staff already registered with this email.", "warning")
            return redirect(url_for("auth.staff_register"))

        # Generate and hash password
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        hashed_password = generate_password_hash(temp_password)

        staff_data = {
            "name": name,
            "email": email,
            "phone": phone,
            "department": department,
            "designation": designation,
            "role": role,
            "password": hashed_password,
            "first_login": True
        }

        mongo.db.staff.insert_one(staff_data)

        # Email credentials
        try:
            mailer.send_credentials(email, name, temp_password)
            flash("Staff registered and credentials sent!", "success")
        except Exception as e:
            flash("Staff saved but email sending failed.", "danger")
            print(e)

        return redirect(url_for("auth.staff_register"))

    return render_template("staff_register.html")




@auth.route('/register_student', methods=["GET", "POST"])
def register_student():
    if request.method == "POST":
        email = request.form.get("email")
        username = request.form.get("username")
        roll_number = request.form.get("roll_number")
        course = request.form.get("course")
        semester = request.form.get("semester")
        department = request.form.get("department")

        # Check if already registered
        from models.database import mongo
        if mongo.db.students.find_one({"email": email}):
            flash("Student with this email already exists.", "warning")
            return redirect(url_for("auth.register_student"))

        # Generate temporary password
        temp_password = ''.join(random.choices(string.ascii_letters + string.digits, k=8))
        hashed_password = generate_password_hash(temp_password)

        student_data = {
            "email": email,
            "username": username,
            "roll_number": roll_number,
            "course": course,
            "semester": semester,
            "department": department,
            "password": hashed_password,
            "role": "student",
            "first_login": True,
            "must_change_password": True
        }

        try:
            mongo.db.students.insert_one(student_data)
            mailer.send_credentials(email=email, username=username, password=temp_password)
            flash("Student registered successfully and credentials emailed.", "success")
        except Exception as e:
            print(f"Error: {e}")
            flash("Student registered, but there was an issue sending email.", "danger")

        return redirect(url_for("auth.register_student"))

    return render_template("register_student.html")









# @auth.route('/login', methods=["GET", "POST"])
# def login():
#     from models.database import mongo

#     if request.method == "POST":
#         email = request.form["email"]
#         password = request.form["password"]

#         user = mongo.db.students.find_one({"email": email})
#         if user and check_password_hash(user["password"], password):
#             session["user_id"] = str(user["_id"])
#             session["username"] = user["username"]
#             session["role"] = user["role"]
#             flash("Logged in successfully!", "success")

#             # After login, redirect to dashboard or camera page
#             return redirect(url_for("dashboard"))

#         flash("Invalid credentials.", "danger")

#     return render_template("login.html")

# @auth.route('/login', methods=["GET", "POST"])
# def login():
#     from models.database import mongo

#     if request.method == "POST":
#         email = request.form["email"]
#         password = request.form["password"]

#         user = mongo.db.students.find_one({"email": email})
#         if user and check_password_hash(user["password"], password):
#             session["user_id"] = str(user["_id"])
#             session["username"] = user["username"]
#             session["role"] = user["role"]
#             flash("Logged in successfully!", "success")

#             # Redirect to actual student dashboard route
#             return redirect(url_for("dashboard"))

#         flash("Invalid credentials.", "danger")

#     return render_template("login.html")


@auth.route('/login', methods=["GET", "POST"])
def login():
    from models.database import mongo

    if request.method == "POST":
        email = request.form["email"]
        password = request.form["password"]

        user = mongo.db.students.find_one({"email": email})
        if user and check_password_hash(user["password"], password):
            session["user_id"] = str(user["_id"])
            session["username"] = user.get("username", "User")
            session["role"] = user.get("role", "student")  # safe access
            flash("Logged in successfully!", "success")

            return redirect(url_for("dashboard"))

        flash("Invalid credentials.", "danger")

    return render_template("login.html")




@auth.route('/forgot-password', methods=['GET', 'POST'])
def forgot_password():
    if request.method == 'POST':
        email = request.form['email']
        from models.database import mongo
        student = mongo.db.students.find_one({'email': email})

        if student:
            token = str(uuid.uuid4())
            mongo.db.reset_tokens.insert_one({'user_id': student['_id'], 'token': token})
            reset_url = url_for('auth.reset_password', token=token, _external=True)

            msg = Message('Password Reset Link',
                          sender=current_app.config['MAIL_USERNAME'],
                          recipients=[email])
            msg.body = f'Click this link to reset your password: {reset_url}'
            mail.send(msg)

            flash('Password reset email sent!', 'info')
        else:
            flash('Email not found', 'danger')

    return render_template('forgot_password.html')


@auth.route('/reset-password/<token>', methods=['GET', 'POST'])
def reset_password(token):
    from models.database import mongo
    token_data = mongo.db.reset_tokens.find_one({'token': token})
    if not token_data:
        flash('Invalid or expired reset link', 'danger')
        return redirect(url_for('auth.login'))

    if request.method == 'POST':
        new_password = request.form['new_password']
        hashed = generate_password_hash(new_password)
        mongo.db.students.update_one(
            {'_id': token_data['user_id']},
            {'$set': {'password': hashed, 'first_login': False}}
        )
        mongo.db.reset_tokens.delete_one({'_id': token_data['_id']})
        flash('Password reset successfully. Please login.', 'success')
        return redirect(url_for('auth.login'))

    return render_template('reset_password.html')



@auth.route("/logout")
def logout():
    session.pop("user", None)
    session.pop("username", None)
    flash("Logged out successfully!", "info")
    return redirect(url_for("auth.login"))




