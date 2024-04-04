from flask import Flask, render_template, request, redirect, url_for, session
from Controllers.UserController import UserController
from Controllers.PrefController import PrefController
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
        if user:
            session['username'] = username
            session['name'] = fullname
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
def p_appoint():
    return render_template('patient_appointment.html')

@app.route('/admin-appointment')
def a_appoint():
    return render_template('admin_appointmentt.html')

if __name__ == '__main__':
    app.run(debug=True)
