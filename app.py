from flask import Flask, render_template, request, redirect, url_for, session
from Controllers.UserController import UserController
from Controllers.PrefController import PrefController
from Controllers.SchedulingModel import SchedulingModel
from Controllers.ReportController import ReportController
from Controllers.AppController import AppController
from Controllers.NotificationController import NotificationController
from Controllers.Triage import Triage
from Controllers.RuleBased import RuleBased
from datetime import datetime
import secrets
import string
import threading
import json


app = Flask(__name__)

def generate_secret_key(length=24):
    characters = string.ascii_letters + string.digits + string.punctuation
    secret_key = ''.join(secrets.choice(characters) for _ in range(length))
    return secret_key

app.secret_key = generate_secret_key()

@app.route('/')
def index():
    return redirect(url_for('login'))

@app.route('/register', methods=['GET'])
def register_form():
    return render_template('create_account.html')

@app.route('/patient-main')
def patient_main():
    if 'username' in session:
        fullname = session['name'] 
        return render_template('patient_main.html', username=fullname) 
    else: 
        return redirect(url_for('login'))

@app.route('/admin-main')
def admin_main():
    if 'username' in session: 
        fullname = session['name']  
        return render_template('admin_main.html', username=fullname) 
    else:
        return redirect(url_for('login'))
    
@app.route('/register', methods=['POST'])
def register():
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    username = request.form.get('username')
    password = request.form['password']
    confirm_password = request.form['confirm_password']
    account_type = 'Patient'
    gender = request.form.get('gender')
    dob = request.form['dob']
    phone = request.form['phone']
    email = request.form['email']
    if password != confirm_password:
        return render_template('create_account.html', error_message="Passwords do not match")
    [registration_message, user] = UserController.register_user(first_name, last_name, username, password, account_type, gender, dob, phone, email)
    
    if registration_message == "User registered successfully, Please Select Preferences":
        return render_template('preference.html', error_message=registration_message, user_id = user)
    else:
        return render_template('create_account.html', error_message=registration_message)

@app.route('/preferences', methods=['POST'])
def submit_pref():
    
    user_id = request.form.get('user_id')
    doctor = request.form.get('doctor')
    time = request.form.get('time')
    location = request.form.get('location')
    preference_type = request.form.get('preference-type')
    
    doctor_rank = request.form.get('doctor-rank')
    time_rank = request.form.get('time-rank')
    location_rank = request.form.get('location-rank')
    type_rank = request.form.get('type-rank')
    
   
    prefmessage = PrefController.submit_preferences(user_id, doctor, time, location, preference_type)
    prefmessage = PrefController.submit_ranks(user_id, doctor_rank, time_rank, location_rank,type_rank)

    
    if prefmessage == "Preferences submitted Succesfully":
        NotificationController.send_account_creation_notification(user_id)
        return render_template('login.html', error_message=prefmessage)
    else: 
        return render_template('preference.html', error_message=prefmessage)

    
@app.route('/register-admin', methods=['GET', 'POST'])
def register_admin():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        confirm_password = request.form['confirm_password']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        account_type = 'Administrator'
        if password != confirm_password:
            return render_template('create_admin.html', error_message="Passwords do not match")
        admin_message = UserController.register_admin(username, password, first_name, last_name,account_type)
        if admin_message == "Administrator account registered successfully!":
            return render_template('login.html', error_message=admin_message)
        else:
            return render_template('create_admin.html', error_message=admin_message)
    else:    
        return render_template('create_admin.html')

# Route for selecting account type
@app.route('/select-account-type')
def select_account_type():
    return render_template('account_type.html')


@app.route('/login', methods=['GET','POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = UserController.check_credentials(username, password)
        fullname = UserController.get_fullname(username, password)
        user_id = UserController.get_id(username, password)
        if user:
            session['username'] = username
            session['name'] = fullname
            session['user_id'] = user_id
            if user['account_type'] == 'Administrator':
                return redirect(url_for('admin_main'))
            elif user['account_type'] == 'Patient':
                return redirect(url_for('patient_main'))
            else:
                error_message = "Invalid account type."
                return render_template('login.html', error_message=error_message)
        else:
            error_message = "Invalid username or password. Please try again."
            return render_template('login.html', error_message=error_message)
    else:
        return render_template('login.html')

@app.route('/logout')
def logout():
    # Clear the session upon logout
    session.pop('username', None)
    return redirect(url_for('login'))

@app.route('/patient-appointment')
def patient_appointment():
    try: 
        past_appointments = AppController.get_past_appointments(session['user_id'])
        past_appointments = AppController.remove_reviewed_appointments(past_appointments)
        upcoming_appointments = AppController.get_upcoming_appointments(session['user_id'])

        

        if upcoming_appointments == []:
            nextmessage = "No upcoming appointments"
        else: 
            for appointment in upcoming_appointments:
        # Convert AppointmentTime to AM/PM format
                appointment_time = datetime.strptime(str(appointment['AppointmentTime']), '%H:%M:%S').strftime('%I:%M %p')
                
                # Format AppointmentDate to have the month in words
                appointment_date = datetime.strptime(str(appointment['AppointmentDate']), '%Y-%m-%d').strftime('%B %d, %Y')
                appointment['AppointmentTime'] = appointment_time
                appointment['AppointmentDate'] = appointment_date
            nextmessage = ""
        if past_appointments == []:
            othermessage = "No past appointments to provide feedback"
        else: 
            for appointment in past_appointments:
        # Convert AppointmentTime to AM/PM format
                appointment_time = datetime.strptime(str(appointment['AppointmentTime']), '%H:%M:%S').strftime('%I:%M %p')
                
                # Format AppointmentDate to have the month in words
                appointment_date = datetime.strptime(str(appointment['AppointmentDate']), '%Y-%m-%d').strftime('%B %d, %Y')
                appointment['AppointmentTime'] = appointment_time
                appointment['AppointmentDate'] = appointment_date
                othermessage = ""
        return render_template('patient_appointment.html', nextmessage = nextmessage, othermessage = othermessage, past_appointments=past_appointments, upcoming_appointments=upcoming_appointments)
    except Exception as e:
        return render_template('login.html', error_message = str(e))
    # Render the template and pass the appointments data to it

@app.route('/manage_users')
def manage_users():
    # Get all users
    users = UserController.get_all_users()
    # Render the template with users data
    return render_template('manage_users.html', users=users)

@app.route('/user_preferences')
def user_preferences():
    # Get all users
    preferences = PrefController.get_preference(session['user_id'])
    # Render the template with users data
    return render_template('user_preferences.html', preferences=preferences)
    
@app.route('/admin-appointment')
def admin_appointment():
    appointments = AppController.get_appointments()
    for appointment in appointments:
        time_str = str(appointment['AppointmentTime'])
            # Convert time string to datetime object to use strftime
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
            # Format time in AM/PM format
        appointment['AppointmentTime'] = time_obj.strftime("%I:%M %p")

    return render_template('admin_appointmentt.html', appointments=appointments)

@app.route('/view-appointment', methods=['POST'])
def view_appointment():
        appointment_id = request.form['appointment_id']
        return redirect(url_for('admin_view_appointment', appointment_id=appointment_id))

@app.route('/admin-view-appointment/<appointment_id>', methods=['GET', 'POST'])
def admin_view_appointment(appointment_id):
        if request.method == 'POST':
        # Check if the cancel button was clicked
            if request.form.get('action') == 'cancel':
            # Call the method to cancel the appointment
                AppController.cancel_appointment(appointment_id)
                appointments = AppController.get_appointments()
                for appointment in appointments:
                    time_str = str(appointment['AppointmentTime'])
            # Convert time string to datetime object to use strftime
                    time_obj = datetime.strptime(time_str, '%H:%M:%S')
            # Format time in AM/PM format
                    appointment['AppointmentTime'] = time_obj.strftime("%I:%M %p")
                
                return render_template('admin_appointmentt.html', appointments=appointments)
        appointment_details = AppController.get_appointment_details(appointment_id)
        formatted_date = appointment_details['AppointmentDate'].strftime('%A, %B %d, %Y')
        appointment_details['AppointmentDate'] = formatted_date
        user_id = AppController.get_user_from_app(appointment_id)
        if user_id == False:
            patientname = "N/A"
            user_details = {'patientname': 'N/A', 'Email': 'N/A', 'PhoneNumber': 'N/A'}
        else:
            user_details = UserController.get_user_details(user_id)
            patientname = UserController.get_patient_name(user_id)
        
        return render_template('Admin_view_appointment.html', appointment_id = appointment_id, appointment_details=appointment_details, user_details=user_details, patientname=patientname)



@app.route('/add-appointment', methods=['GET'])
def add_appointment():
    return render_template('add_appointment.html')


@app.route('/submit-appointment', methods=['POST'])
def submit_appointment():
  
    date = request.form['date']
    time = request.form['time']
    location = request.form['location']
    doctor = request.form['doctor']

    message = AppController.add_appointment(date,time,location,doctor)
  
    appointments = AppController.get_appointments()
    for appointment in appointments:
        time_str = str(appointment['AppointmentTime'])
            # Convert time string to datetime object to use strftime
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
            # Format time in AM/PM format
        appointment['AppointmentTime'] = time_obj.strftime("%I:%M %p")

    return render_template('admin_appointmentt.html', appointments=appointments, message = message)

@app.route('/modify-appointment/<appointment_id>', methods=['GET', 'POST'])
def modify_appointment(appointment_id):
    if request.method == 'POST':
        date = request.form['date']
        time = request.form['time']
        location = request.form['location']
        doctor = request.form['doctor']
        AppController.modify_appointment(appointment_id, date, time, location, doctor)
        return redirect(url_for('admin_view_appointment', appointment_id = appointment_id))
    else:
        appointment_details = AppController.get_appointment_details_modify(appointment_id)
        return render_template('modify_appointment.html', appointment_id= appointment_id, appointment_details=appointment_details)

@app.route('/provide-feedback/<appointment_id>')
def provide_feedback(appointment_id):
    return render_template('feedback_form.html', appointment_id = appointment_id) 


@app.route('/submit-feedback', methods=['POST'])
def submit_feedback():
    if request.method == 'POST':
        appointment_id = request.form['appointment_id']
        feedback = request.form['feedback']
        message = AppController.submitfeedback(appointment_id,feedback) 
        past_appointments = AppController.get_past_appointments(session['user_id'])
        past_appointments = AppController.remove_reviewed_appointments(past_appointments)
        upcoming_appointments = AppController.get_upcoming_appointments(session['user_id'])
        app = AppController.get_appointment_details(appointment_id)
        NotificationController.send_feedback_received_notification(session['user_id'],app)
        if upcoming_appointments == []:
            nextmessage = "No upcoming appointments"
        else: 
            nextmessage = ""
        if past_appointments == []:
            othermessage = "No past appointments to provide feedback"
        else:
             othermessage = "" 
        return render_template('patient_appointment.html', nextmessage = nextmessage, othermessage = othermessage, message = message, past_appointments=past_appointments, upcoming_appointments=upcoming_appointments)




@app.route('/patient-list/<appointment_id>')
def patient_list(appointment_id):
    appointments = AppController.get_appointments_patient()
    for appointment in appointments:
                appointment_time = datetime.strptime(str(appointment['AppointmentTime']), '%H:%M:%S').strftime('%I:%M %p')
                appointment_date = datetime.strptime(str(appointment['AppointmentDate']), '%Y-%m-%d').strftime('%B %d, %Y')
                appointment['AppointmentTime'] = appointment_time
                appointment['AppointmentDate'] = appointment_date
         

    return render_template('reschedule_list.html', appointments = appointments, appointment__id= appointment_id)

@app.route('/appointment-list')
def apppointment_list():
    appointments = AppController.get_appointments_patient()
    for appointment in appointments:
        time_str = str(appointment['AppointmentTime'])
            # Convert time string to datetime object to use strftime
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
            # Format time in AM/PM format
        appointment['AppointmentTime'] = time_obj.strftime("%I:%M %p")
    return render_template('appointment_list.html', appointments = appointments)


@app.route('/book',  methods=['POST'])
def book():
    if request.method == 'POST':
        appointment_id = request.form['appointment_id']
    return render_template('book_form.html', appointment_id=appointment_id)

@app.route('/book-appointment', methods=['POST'])
def book_appointment():
    if request.method == 'POST':
        appointment_id = request.form['appointment_id']
        priority = request.form['priority']
        type = request.form['type']
        AppController.ScheduleAppointment(appointment_id,priority,type, session['user_id'],'Scheduled')
        past_appointments = AppController.get_past_appointments(session['user_id'])
        past_appointments = AppController.remove_reviewed_appointments(past_appointments)
        upcoming_appointments = AppController.get_upcoming_appointments(session['user_id'])
        if upcoming_appointments == []:
            nextmessage = "No upcoming appointments"
        else: 
            nextmessage = ""
        if past_appointments == []:
            othermessage = "No past appointments to provide feedback"
        else:
             othermessage = "" 
        app = AppController.get_appointment_details(appointment_id)

        NotificationController.send_schedule_notification(session['user_id'],app)
        

    return render_template('patient_appointment.html', message = "Appointment Booked", nextmessage = nextmessage, othermessage = othermessage, past_appointments=past_appointments, upcoming_appointments=upcoming_appointments)



@app.route('/auto_book')
def auto_book():
    question_list = AppController.retrieve_emergency_questions()
    return render_template('triage.html',question_list=question_list)

@app.route('/triage-two')
def triage_two():
    question_list = AppController.retrieve_triage2_questions()
    return render_template('triage_two.html',question_list=question_list)

@app.route('/triage-three')
def triage_three():
    question_list = AppController.retrieve_appointment_questions()
    return render_template('triage_three.html', question_list=question_list)

@app.route('/submit-triage', methods=['POST'])
def submit_triage():
    # Collect form data
    emergency_data = {}
    L1Response = []
    L2Response=['no']
    L3Response=[]
    L4Response=[0,[]]
    closestLocation =request.form['location']


    for i in range(1, 9):
        checkbox_name = f"emergency{i}"
        emergency_data[checkbox_name] = request.form.get(checkbox_name, "No")
        L1Response.append(emergency_data[checkbox_name])

    triage_level = Triage.triagelevel(L1Response,L2Response,L3Response,L4Response)

    pref = PrefController.get_preference(session['user_id'])
    
    

    appointment = RuleBased.schedule_appointment(session['user_id'], pref,triage_level,closestLocation)
    app = AppController.get_appointment_details(appointment['AppointmentID'])
    location_email = AppController.getLocationEmail(closestLocation)
    NotificationController.send_incoming_patient_notification(session['user_id'],closestLocation,app,location_email,triage_level)
    NotificationController.send_schedule_notification(session['user_id'],app)
    appointment_time = datetime.strptime(str(appointment['AppointmentTime'])[-8:], '%H:%M:%S').strftime('%I:%M %p')

    if triage_level == 1:
    # Add your further processing here
    
        return render_template('urgent.html', time = appointment_time, location = closestLocation)
    else: 
        return redirect(url_for('patient_appointment'))
    
@app.route('/submit-triage-two', methods=['POST'])
def submit_triage_two():
    # Collect form data
    emergency_data = {}
    L1Response = []
    L2Response=['no']
    L3Response=[]
    L4Response=[0,[]]
    closestLocation =request.form['location']
    pref = PrefController.get_preference(session['user_id'])



    for i in range(1, 5):
        checkbox_name = f"triage{i}"
        emergency_data[checkbox_name] = request.form.get(checkbox_name, "No")
        L2Response.append(emergency_data[checkbox_name])

    triage_level = Triage.triagelevel(L1Response,L2Response,L3Response,L4Response)
    
    
    appointment = RuleBased.schedule_appointment(session['user_id'], pref,triage_level,closestLocation)
    app = AppController.get_appointment_details(appointment['AppointmentID'])
    location_email = AppController.getLocationEmail(closestLocation)
    NotificationController.send_incoming_patient_notification(session['user_id'],closestLocation,app,location_email,triage_level)
    NotificationController.send_schedule_notification(session['user_id'],app)
    appointment_time = datetime.strptime(str(appointment['AppointmentTime'])[-8:], '%H:%M:%S').strftime('%I:%M %p')
    
    if triage_level == 2:
    # Add your further processing here
    
        return render_template('urgent.html', time = appointment_time, location = closestLocation)
    else: 
        return redirect(url_for('patient_appointment'))






@app.route('/submit-triage-three', methods=['POST'])
def submit_triage_three():
    
   
    form_data = request.form.to_dict()
    q1 = form_data['question1']
    q2 = form_data['question2']
    q3 = form_data['question3']
    L3response = [q1,q2,q3]
    vitals = {}
    if form_data['systolicPressure'] != '':
        vitals['cystolic_blood_pressure'] = int(form_data['systolicPressure'])
    if form_data['diastolicPressure'] != '':                                            
        vitals['diastolic_blood_pressure'] = int(form_data['diastolicPressure'])
    if form_data['heartRate'] != '':
        vitals['heart_rate'] = int(form_data['heartRate'])
    if form_data['respiratoryRate'] != '':
        vitals['respiratory_rate'] = int(form_data['respiratoryRate'])
    if form_data['temperature'] != '':
        vitals['temperature'] = int(form_data['temperature'])
    if form_data['oxygenSaturation'] != '':
        vitals['oxygen_saturation'] = int(form_data['oxygenSaturation'])
    if form_data['age'] == '':
        theage = 0
    else: 
        theage = int(form_data['age'])*12
    L4response =[theage,vitals]
    L1response = ['no']
    L2response = ['no']



    triage_level = Triage.triagelevel(L1response,L2response,L3response,L4response)
    pref = PrefController.get_preference(session['user_id'])
    appointment = RuleBased.schedule_appointment(session['user_id'], pref,triage_level,pref['Location'])
    app = AppController.get_appointment_details(appointment['AppointmentID'])
    if triage_level == 2:
        appointment_time = datetime.strptime(str(appointment['AppointmentTime'])[-8:], '%H:%M:%S').strftime('%I:%M %p')
        location_email = AppController.getLocationEmail(pref['Location'])
        NotificationController.send_incoming_patient_notification(session['user_id'],pref['Location'],app,location_email,triage_level)
        NotificationController.send_schedule_notification(session['user_id'],app)
        return ([pref['Location'],appointment_time],200)
    else:
        NotificationController.send_schedule_notification(session['user_id'],app)
        return (['triage3','o'], 200)
    
    # Add your further processing here

    

@app.route('/reschedule-appointment', methods=['POST'])
def reschedule_appointment():
    if request.method == 'POST':
        appointment_id = request.form['appointment_id']
        old_appointment = request.form['old_appointment']
        priority = request.form['priority']
        type = request.form['type']
        AppController.OpenAppointment(old_appointment,'Open')
        AppController.ScheduleAppointment(appointment_id,priority,type, session['user_id'],'Scheduled')
        past_appointments = AppController.get_past_appointments(session['user_id'])
        past_appointments = AppController.remove_reviewed_appointments(past_appointments)
        upcoming_appointments = AppController.get_upcoming_appointments(session['user_id'])
        if upcoming_appointments == []:
            nextmessage = "No upcoming appointments"
        else: 
            nextmessage = ""
        if past_appointments == []:
            othermessage = "No past appointments to provide feedback"
        else:
             othermessage = "" 
        old = AppController.get_appointment_details(old_appointment)
        new = AppController.get_appointment_details(appointment_id)

        NotificationController.send_reschedule_notification(session['user_id'],new,old)
        
        
        
    return render_template('patient_appointment.html', message = "Appointment Rescheduled", nextmessage = nextmessage, othermessage = othermessage, past_appointments=past_appointments, upcoming_appointments=upcoming_appointments)
    
    
@app.route('/reschedule',  methods=['POST'])
def reschedule():
    if request.method == 'POST':
        appointment_id = request.form['appointment_id']
        old_appointment = request.form['old_appointment']
    return render_template('reschedule_form.html', appointment_id=appointment_id, old_appointment=old_appointment)

@app.route('/cancel-appointment/<appointment_id>', methods=['GET'])
def cancel_appointment(appointment_id):
        AppController.OpenAppointment(appointment_id, 'Open')
        past_appointments = AppController.get_past_appointments(session['user_id'])
        past_appointments = AppController.remove_reviewed_appointments(past_appointments)
        upcoming_appointments = AppController.get_upcoming_appointments(session['user_id'])
        app = AppController.get_appointment_details(appointment_id)
        NotificationController.send_cancel_notification(session['user_id'],app)
        if upcoming_appointments == []:
            nextmessage = "No upcoming appointments"
        else: 
            nextmessage = ""
        if past_appointments == []:
            othermessage = "No past appointments to provide feedback"
        else:
             othermessage = ""
       
        return render_template('patient_appointment.html', message = "Appointment Cancelled", nextmessage = nextmessage, othermessage = othermessage, past_appointments=past_appointments, upcoming_appointments=upcoming_appointments)
@app.route('/view_profile')
def view_profile():
    user_info_1 = UserController.get_user(session['user_id'])
    user_info_2 = UserController.get_patient(session['user_id'])
    dob = datetime.strptime(str(user_info_2[2]), '%Y-%m-%d').strftime('%B %d, %Y')

    return render_template('profile.html', user=user_info_1, user_2 = user_info_2,dib = dob)
@app.route('/reports')
def reports():
    # Assuming you have a template named 'reports.html'
    return render_template('reports.html')

@app.route('/showreport/<report_type>')
def show_report(report_type):
    report_object = ReportController.get_reports(report_type)
    if report_object:
        report_id = report_object['report_id']
        report_date = report_object['report_date']
        report_data = report_object['report_data']
        generated_at = report_object['generated_at']
       
    else:
        return render_template('reports.html', message = 'This report has not yet been generated')

    if report_type == 'appointment_counts':

        report_data = json.loads(report_data)
        
        return render_template('appointment_counts.html', report_type=report_type,report_data = report_data, report_date = report_date, generated_at = generated_at, report_id = report_id)
    elif report_type == 'patient_demographics':
        report_data = json.loads(report_data)

        return render_template('patient_demographics.html', report_type=report_type,report_data = report_data, report_date = report_date, generated_at = generated_at, report_id = report_id)
    elif report_type == 'appointment_location_counts':
        report_data = json.loads(report_data)


        return render_template('appointment_location_counts.html', report_type=report_type,report_data = report_data, report_date = report_date, generated_at = generated_at, report_id = report_id)
    else: 
        report_data = json.loads(report_data)


        return render_template('appointment_provider_counts.html', report_type=report_type,report_data = report_data, report_date = report_date, generated_at = generated_at, report_id = report_id)


if __name__ == '__main__':
    # Start the ReminderModel in a separate thread
    reminder_thread = threading.Thread(target=SchedulingModel.start)
    reminder_thread.daemon = True  # Set the thread as a daemon so it exits when the main thread exits
    reminder_thread.start()

    # Run the Flask application
    app.run(debug=True)
