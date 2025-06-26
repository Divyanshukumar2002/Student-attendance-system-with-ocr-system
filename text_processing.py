import re
from flask_sqlalchemy import model
from pymongo import mongo_client
from datetime import datetime
from flask.json import jsonify


def fetch_student_details(_id):
    from models.database import mongo
    student_xist = False
    if mongo.db.student_details.find_one({'AD_No':_id}): 
        student_xist = True
    return student_xist

    

def make_attendence(_id):
    from models.database import mongo
    status = "Present"
    today = datetime.now().strftime('%Y-%m-%d hh:mm:ss')
    
    attend_data = {
          'student_id': _id,
          'date': today,
          'status': status      
    }
    if mongo.db.attendance_table.insert_one(attend_data):
        print(attend_data)
        return jsonify({"Status":"Attendence logged in!"})
    
    return "Someting went wrong!"
    

def extract_aadhar_data(text):
    from models.database import mongo
    text = re.sub(r'[^a-zA-Z0-9/\s]', '', text)

    print(text)
    # 1️⃣ Extract Name: Pattern to match 3 capitalized words
    name_pattern = re.compile(r'([A-Z][a-z]+\s[A-Z][a-z]+(?:\s[A-Z][a-z]+)?)')
    name_match = name_pattern.search(text)
    name = name_match.group() if name_match else "Not Found"

    dob_pattern = re.compile(r'\b(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/(19|20)\d{2}\b')
    dob_match = dob_pattern.search(text)
    dob = dob_match.group() if dob_match else "Not Found"

    # 3️⃣ Extract Gender: Matches 'MALE' or 'FEMALE' (case-insensitive)
    gender_pattern = re.compile(r'\b(MALE|FEMALE)\b', re.IGNORECASE)
    gender_match = gender_pattern.search(text)
    gender = gender_match.group().capitalize() if gender_match else "Not Found"

    # 2️⃣ Extract DOB: Matches DDMMYY or DD/MM/YYYY
    ad_no = re.compile(r'(\d{4}\s?\d{4}\s?\d{4})')
    dob_match = ad_no.search(text)
    if dob_match:
        aad_no = dob_match.groups()
        
    else:
        aad_no = "Not Found"

    # ✅ Display the results
    print(f"Name: {name}")
    print(f"DOB: {dob}")
    print(f"Gender: {gender}")
    print(f"AD No: {aad_no[0]}")
    
    data = {}
    
    data['Name'] = name
    data['DOB'] = dob
    data['Gender']= gender
    data['AD_No'] = aad_no[0]
    
    _id = aad_no[0]
    present = fetch_student_details(_id)
    
    if present:
        make_attendence(_id)
    else:
        mongo.db.student_details.insert_one(data)


    return name, dob, gender, aad_no[0]

    if mongo.db.attend.insert(data):
        return "Attendence logged in!"
    return "User Not Exist"
    
    
def extract_pan_data(text):
    from models.database import mongo

    text = re.sub(r'[^a-zA-Z0-9/\s]', '', text)

    text = " ".join([i for i in text.replace("\n"," ").strip().split(" ") if len(i)>3])

    print(text)
    # Regular expression patterns
    pan_pattern = re.compile(r'[A-Z]{5}[0-9]{4}')  # Pattern for PAN card
    name_pattern = re.compile(r'[A-Z][A-Z]+\s[A-Z][A-Z]+(?:\s[A-Z]+)?')  # Pattern for Names

    # Extracting PAN and names
    pan_match = pan_pattern.findall(text)
    name_matches = name_pattern.findall(text)

    print(name_matches)
    dob_pattern = re.compile(r'\b(0[1-9]|[12][0-9]|3[01])/(0[1-9]|1[0-2])/(19|20)\d{2}\b')
    dob_match = dob_pattern.search(text)
    dob = dob_match.group() if dob_match else "Not Found"

    if len(name_matches)>=2:
        name = name_matches[0]
        father_name = name_matches[1]
    else:
        name = "Not found"
        father_name = "Not Found"

    print(f"DOB: {dob}")
    if len(pan_match)>0:
        pan_no = pan_match[0]
    else:
        pan_no = "Not Found"
    
    print(f"PAN Number: {pan_no}")

    print(f"PAN Holder Name: {name}")
    print(f"Father's Name: {father_name}")
    
    data ={}
    data['PAN_Number'] = pan_no[0]
    data['PAN_Holder_Name'] = name
    data['DOB']= dob
    data['Father_Name'] = father_name
    
    _id = pan_no[0]
    present = fetch_student_details(_id)
    
    if present:
        make_attendence(id)
    else:

            mongo.db.student_details.insert_one(data)

    
    # Combine results
    return pan_no , name, father_name, dob
    
    

def profile_data():
    from models.database import mongo
    
    return list(mongo.db.student_details.find())