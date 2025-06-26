
from flask import Flask, render_template, request, flash, redirect, url_for, session, jsonify, Response
from auth import auth
from camera import VideoCamera
from models.database import init_db, data_collection
import pytesseract
from PIL import Image
import cv2
from text_processing import extract_pan_data, extract_aadhar_data, profile_data
from bson.objectid import ObjectId
from bson.errors import InvalidId

import sys
from flask_mail import Mail
from extensions import mail 
from datetime import datetime
# from routes.student_routes import student





app = Flask(__name__)
app.secret_key = "super_secret_key"

app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USERNAME'] = 'divyanshuelgoss@gmail.com'                                                                                                                                                               
app.config['MAIL_PASSWORD'] = 'cphe keee utbd sksq'







# Initialize Database 
init_db(app)

# Register Blueprints
app.register_blueprint(auth, url_prefix="/auth")



video_camera = None
is_capturing = False

# Home Page
@app.route("/")
def index():
    return render_template("index.html")




@app.route("/dashboard")
def dashboard():
    if "username" in session:
        return render_template("dashboard.html", username=session["username"])
    return redirect(url_for("auth.login"))
    
@app.route('/super_admin_dashboard')
def super_admin_dashboard():
    return render_template('super_admin_dashboard.html')




@app.route('/student/Dashboard')
def student_Dashboard():
    from models.database import mongo
    student_id = session.get('student_id')
    student = mongo.db.students.find_one({'_id': student_id})
    records = mongo.db.attendance_table.find({'student_id': student_id})

    dates = []
    attendance_data = []

    for r in records:
        dates.append(r['date'])
        attendance_data.append(1 if r['status'] == 'Present' else 0)

    return render_template('student_Dashboard.html', student=student, dates=dates, attendance_data=attendance_data)

@app.route('/student/settings', methods=['GET', 'POST'])
def student_settings():
    student_id = session.get('student_id')
    from models.database import mongo
    student = mongo.db.students.find_one({'_id': student_id})
    return render_template('settings.html', student=student)

@app.route('/student/update_profile', methods=['POST'])
def update_profile():
    from models.database import mongo
    student_id = session.get('student_id')
    mongo.db.students.update_one({'_id': student_id}, {
        "$set": {
            "email": request.form['email'],
            "mobile": request.form['mobile']
        }
    })
    return redirect('/student/settings')

@app.route('/student/reset_password', methods=['POST'])
def reset_password():
    from models.database import mongo
    student_id = session.get('student_id')
    new_pass = request.form['new_password']
    mongo.db.students.update_one({'_id': student_id}, {"$set": {"password": new_pass}})
    return redirect('/student/settings')






   





@app.route("/profile")
def profile(): 
    if "username" in session:
        # Fetch extracted data from MongoDB
        user_data = profile_data()
        return render_template("profile.html", user_data=user_data) 
    return redirect(url_for("auth.update"))

@app.route('/search')
def search():
    query = request.args.get('query', '').strip()

    # Search logic: match against Name or Aadhaar/PAN numbers (case-insensitive)
    from models.database import mongo
    search_results = list(mongo.db.student_details.find({
        "$or": [
            {"Name": {"$regex": query, "$options": "i"}},
            {"AD_No": {"$regex": query, "$options": "i"}},
            {"PAN_No": {"$regex": query, "$options": "i"}}
        ]
    }))

    return render_template('profile.html', user_data=search_results)

@app.route("/about")
def about():
    return render_template("about.html")


# @app.route('/attendance', methods=['GET', 'POST'])
# def attendance():
#     from models.database import mongo  # import if needed

#     if request.method == 'POST':
#         # Your attendance marking logic here
#         msg = " Attendance marked successfully!"
#         return redirect(url_for("attendance.html", msg=msg))

#     else:
#         # GET request – show all attendance records
#         records = list(mongo.db.attendance_table.find())
#         return render_template("attendance.html", records=records)

@app.route('/attendance', methods=['GET', 'POST'])
def attendance():
    from models.database import mongo
    if request.method == 'POST':
        student_id = request.form.get('student_id')
        status = request.form.get('status')  # e.g. "Present" or "Absent"
        date = request.form.get('date')
        time = request.form.get('time')

        if student_id and status and date and time:
            mongo.db.attendance_table.insert_one({
                'student_id': student_id,
                'status': status,
                'date': date,
                'time': time
            })
            flash("Attendance marked successfully!", "success")
        else:
            flash("Missing required fields!", "danger")

        return redirect(url_for('attendance'))

    # GET request – show all attendance records
    records = list(mongo.db.attendance_table.find())
    present_days = mongo.db.attendance_table.count_documents({'status': 'Present'})
    absent_days = mongo.db.attendance_table.count_documents({'status': 'Absent'})

    return render_template("attendance.html",
                           records=records,
                           present_days=present_days,
                           absent_days=absent_days)
    
    
@app.route('/attendance-summary')
def attendance_summary():
    from models.database import mongo
    total_students = mongo.db.attendance_table.distinct('student_id')
    total_students_count = len(total_students)

    total_present = mongo.db.attendance_table.count_documents({'status': 'Present'})

    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    return render_template("attendance_summary.html",
                           total_students_count=total_students_count,
                           total_present=total_present,
                           current_time=current_time)

@app.route('/attenshow', methods=['GET'])
def attenshow():
    return render_template('attenshow.html', content=" Attendance logged in successfully!")

    




# Delete User Dat
@app.route("/update/<id>", methods=["GET", "POST"])
def update_user(id):
    from models.database import mongo
    student_collection = mongo.db.student_details  # adjust this to your actual MongoDB setup

    if request.method == 'POST':
        # Update data
        student_collection.update_one(
            {'_id': ObjectId(id)},
            {
                "$set": {
                    'Name': request.form['name'],
                    'DOB': request.form['dob'],
                    'Gender': request.form['gender'],
                    'AD_No': request.form['id_no'] if request.form['card_type'] == 'aadhaar' else None,
                    'PAN_No': request.form['id_no'] if request.form['card_type'] == 'pan' else None
                }
            }
        )
        return redirect(url_for('profile'))
    

    # GET request - fetch user for form
    user = student_collection.find_one({'_id': ObjectId(id)})
    return render_template("update.html", user=user)


@app.route('/delete/<id>', methods=['GET'])
def delete_user(id):
    from models.database import mongo
    mongo.db.student_details.delete_one({'_id': ObjectId(id)})
    return redirect(url_for('profile'))  # Redirect back to the profile page


# Open Video Feed
@app.route("/video_feed")
def video_feed():
    global video_camera
    if video_camera is None:
        video_camera = VideoCamera()
     
    def generate_frames():
        while True:
            frame = video_camera.get_frame()
            if frame:
                yield (b"--frame\r\n"
                       b"Content-Type: image/jpeg\r\n\r\n" + frame + b"\r\n\r\n")
            else:
                break

    return Response(generate_frames(), mimetype="multipart/x-mixed-replace; boundary=frame")

# Capture and Extract Aadhaar/PAN Data
@app.route("/capture", methods=["POST"])
def capture():
    global video_camera
    if "username" not in session:
        return redirect(url_for("auth.login"))

    card_type = request.form.get("card_type")
    filename = "aadhar2.jpeg"
    image_path = video_camera.capture_image(filename)

    # Extract text using Tesseract
    config = r'--oem 1 --psm 6 -l eng'
    image_path = 'static/aadhar2.jpeg'
    image = cv2.imread(image_path)
    # gray_image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    

    text = pytesseract.image_to_string(image, config=config)
    print(text)
    print(f"Card type : {card_type}")

    # Identify Card Type and Extract Data
    if card_type == "aadhaar":
        data = extract_aadhar_data(text)
    elif card_type == "pan":
        data = extract_pan_data(text)
    else:
        data = {"Error": "Invalid card type"}

    return redirect(url_for('profile')) 

if __name__ == "__main__":
    app.run(debug=False)

