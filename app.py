from flask import Flask, render_template, request, redirect, url_for, session
from Controllers.UserController import UserController
from Controllers.PrefController import PrefController
from Controllers.AppController import AppController
from datetime import datetime
import secrets
import string

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
    
   
    prefmessage = PrefController.submit_preferences(user_id, doctor, time, location, preference_type)
    
    if prefmessage == "Preferences submitted Succesfully":
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
            nextmessage = ""
        if past_appointments == []:
            othermessage = "No past appointments to provide feedback"
        else: othermessage = ""
        return render_template('patient_appointment.html', nextmessage = nextmessage, othermessage = othermessage, past_appointments=past_appointments, upcoming_appointments=upcoming_appointments)
    except Exception as e:
        return render_template('login.html', error_message = "Session Timed Out, Please Login Again")
    # Render the template and pass the appointments data to it
    
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
        time_str = str(appointment['AppointmentTime'])
            # Convert time string to datetime object to use strftime
        time_obj = datetime.strptime(time_str, '%H:%M:%S')
            # Format time in AM/PM format
        appointment['AppointmentTime'] = time_obj.strftime("%I:%M %p")
         

    return render_template('patient_list.html', appointments = appointments, appointment__id= appointment_id)

@app.route('/reschedule-appointment', methods=['POST'])
def reschedule_appointment():
    if request.method == 'POST':
        appointment_id = request.form['appointment_id']
        old_appointment = request.form['old_appointment']
        priority = request.form['priority']
        type = request.form['type']
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
        
        AppController.OpenAppointment(old_appointment,'Open')
        AppController.ScheduleAppointment(appointment_id,priority,type, session['user_id'],'Scheduled')
        
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
        if upcoming_appointments == []:
            nextmessage = "No upcoming appointments"
        else: 
            nextmessage = ""
        if past_appointments == []:
            othermessage = "No past appointments to provide feedback"
        else:
             othermessage = ""
       
        return render_template('patient_appointment.html', message = "Appointment Cancelled", nextmessage = nextmessage, othermessage = othermessage, past_appointments=past_appointments, upcoming_appointments=upcoming_appointments)

if __name__ == '__main__':
    app.run(debug=True)
