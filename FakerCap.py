from faker import Faker
import random
from datetime import datetime, timedelta

fake = Faker()

# Function to generate random dates within a given time range
def generate_random_datetime(start_time, end_time):
    # Ensure the start_time and end_time are datetime objects
    if isinstance(start_time, str):
        start_time = datetime.strptime(start_time, '%Y-%m-%d %H:%M:%S')
    if isinstance(end_time, str):
        end_time = datetime.strptime(end_time, '%Y-%m-%d %H:%M:%S')

    # Calculate the total number of 30-minute intervals between start_time and end_time
    delta = end_time - start_time
    total_intervals = int(delta.total_seconds() // (30 * 60))

    # Generate a random number of intervals
    random_interval = random.randint(0, total_intervals)

    # Calculate the random datetime by adding the random_interval to the start_time
    random_datetime = start_time + timedelta(minutes=30 * random_interval)

    return random_datetime

# Function to generate usernames based on first letter of first name and last name
def generate_username(first_name, last_name):
    return f"{first_name[0].lower()}{last_name.lower()}"

# Function to generate emails based on first and last names
def generate_email(first_name, last_name):
    return f"{first_name.lower()}{last_name.lower()}{fake.random_number(digits=2)}@example.com"

# Function to generate SQL INSERT statements for User and Patient tables
def generate_user_data(num_administrators, num_patients):
    user_data = []
    patient_data = []
    admin_data = []

    
    # Generating administrators
    for i in range(1, num_administrators + 1):
        user_id = f'AD{i:03d}'
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = generate_username(first_name, last_name)
        password = fake.password()
        account_type = 'Administrator'
        email = generate_email(first_name, last_name)
        user_data.append((user_id, username, password, first_name, last_name, account_type))
        admin_data.append((user_id))
        
    # Generating patients
    for i in range(1, num_patients + 1):
        user_id = f'PA{i:03d}'
        first_name = fake.first_name()
        last_name = fake.last_name()
        username = generate_username(first_name, last_name)
        password = fake.password()
        account_type = 'Patient'
        gender = fake.random_element(elements=('Male', 'Female'))
        date_of_birth = fake.date_of_birth(minimum_age=18, maximum_age=90).strftime('%Y-%m-%d')
        phone_number = f'876-{fake.random_int(min=100, max=999)}-{fake.random_int(min=1000, max=9999)}'
        email = generate_email(first_name, last_name)
        user_data.append((user_id, username, password, first_name, last_name, account_type))
        patient_data.append((user_id, gender, date_of_birth, phone_number, email))
        
    return user_data, patient_data, admin_data

def generate_appointment_data(num_records, num_patients):
    appointment_data = []
    for i in range(1, num_records + 1):
        appointment_id = f'AP{i:03d}'
        patient_id = f'PA{random.randint(1, num_patients):03d}'
        priority_level = fake.random_int(min=1, max=5)
        start_datetime = datetime.now()
        end_datetime = start_datetime + timedelta(days=30)

        random_date = generate_random_datetime(start_datetime, end_datetime)

        start_time = random_date.replace(hour=7, minute=0, second=0)
        end_time = random_date.replace(hour=21, minute=30, second=0)
        appointment_time = generate_random_datetime(start_time, end_time)
        appointment_type = random.choice(['In-Person', 'Phone Call', 'Video Call','In-Person','In-Person','In-Person','In-Person','In-Person'])
        appointment_location = fake.random_element(elements=('Uwi Hospital', 'Center C', 'Family Care Medical Centre', 'Andrews Memorial'))
        provider = fake.random_element(elements=('Dr. Smith', 'Dr. Johnson', 'Dr. Lee', 'Dr. White', 'Dr. Brown'))
        # Determine appointment status
        appointment_status =  'Open'
        if appointment_status == 'Open':
            patient_id = 'NULL'  
            appointment_type = 'NULL'
            priority_level = 0
        appointment_data.append((appointment_id, priority_level, appointment_time, appointment_location, appointment_type, appointment_status, patient_id,provider))
    return appointment_data

def generate_patient_preference_data(num_records):
    preference_data = []
    rank_data = []
    patient_ids = [f'PA{i:03d}' for i in range(1, num_records + 1)]
    
    for i in range(1, num_records + 1):
        patient_id = random.choice(patient_ids)
        preference_id = f'PR{i:03d}'
        rank_id = "RA"+preference_id[2:]
        type_rank = random.choice([1, 2, 3, 4, 5])
        provider_rank = random.choice([1, 2, 3, 4, 5])
        location_rank = random.choice([1, 2, 3, 4, 5])
        time_of_day_rank = random.choice([1, 2, 3, 4, 5])
        rank_data.append((patient_id, rank_id, type_rank, provider_rank, location_rank, time_of_day_rank))
        preference_type = random.choice(['In-Person', 'Phone Call', 'Video Call','In-Person','In-Person','In-Person','In-Person','In-Person'])
        provider = fake.random_element(elements=('Dr. Smith', 'Dr. Johnson', 'Dr. Lee', 'Dr. White', 'Dr. Brown'))
        location = fake.random_element(elements=('Uwi Hospital', 'Family Care Medical Centre', 'Center C', 'Andrews Memorial'))
        time_of_day = fake.random_element(elements=('Morning', 'Afternoon', 'Evening'))

        preference_data.append((patient_id, preference_id, preference_type, provider, location, time_of_day))

        # Remove chosen patient ID to avoid duplication
        patient_ids.remove(patient_id)

    return preference_data, rank_data




# Generate data
num_administrators = 5
num_patients = 100
num_appointments = 200

user_data, patient_data, admin_data = generate_user_data(num_administrators, num_patients)
admin_user_ids = [user[0] for user in user_data[:num_administrators]]  # Extract admin user IDs
patient_user_ids = [user[0] for user in user_data[num_administrators:]]  # Extract patient user IDs
appointment_data = generate_appointment_data(num_appointments, num_patients)
preference_data, rank_data = generate_patient_preference_data(num_patients)


with open('insertionfile.sql', 'w') as file:
    # Insert dummy data into the User table
    file.write("INSERT INTO User (UserID, Username, UserPassword, FirstName, LastName, AccountType) \nVALUES\n \n")
    for user in user_data:
        if user == user_data[-1]:
            file.write(f"{user};\n \n")
            file.write("\n")
        else:
            file.write(f"{user},\n")

    # Insert dummy data into the Patient table
    file.write("INSERT INTO Patient (UserID, Gender, DateOfBirth, PhoneNumber, Email) \nVALUES\n \n")
    for patient in patient_data:
        if patient == patient_data[-1]:
            file.write(f"{patient};\n \n")
            file.write("\n")
        else:
            file.write(f"{patient},\n")

    file.write("INSERT INTO Appointment (appointmentID, priorityLevel, appointmentTime, appointmentLocation, appointmentType, appointmentStatus, userID, Provider) \nVALUES\n \n")
    for appointment in appointment_data:
        file.write('(')
        for i, value in enumerate(appointment):
            if value == 'NULL':
                file.write(value)
            else:
                file.write(f"'{value}'")
            
            if i < len(appointment) - 1:
                file.write(', ')
        
        file.write(')')
        
        if appointment == appointment_data[-1]:
            file.write(';\n \n')
            file.write('\n')
        else:
            file.write(',\n')


    file.write("INSERT INTO Preference (UserID, PreferenceID, Type, Provider, Location, TimeOfDay) \nVALUES\n \n")
    for preference in preference_data:
        if preference_data[-1]== preference:
            file.write(f"{preference};\n \n")
            file.write("\n")
        else: 
            file.write(f"{preference},\n")

    file.write("INSERT INTO PreferenceRank (UserID, RankID, Type_rank, Provider_rank, Location_rank, TimeOfDay_rank) \nVALUES\n \n")
    for rank in rank_data:
        if rank_data[-1]== rank:
            file.write(f"{rank};\n \n")
            file.write("\n")
        else: 
            file.write(f"{rank},\n")

    file.write("INSERT INTO Administrator (UserID) \nVALUES\n")
    for admin_id in admin_data:
        if admin_id == admin_data[-1]:
            file.write(f"('{admin_id}');\n \n")
        else:
            file.write(f"('{admin_id}'),\n")


    file.write('''   
INSERT INTO Location (LocationName, LocationEmail)
VALUES
('Uwi Hospital', 'rumchat21@gmail.com'),
('Family Care Medical Centre', 'rumchat21@gmail.com'),
('Center C', 'rumchat21@gmail.com'),
('Andrews Memorial', 'rumchat21@gmail.com');''')
    
    file.write('''
               
INSERT INTO emergency_questions (question_text) VALUES
 ('Do you or someone else have a life-threatening medical emergency at this moment?'),
 ('Are you experiencing symptoms such as severe chest pain, difficulty breathing, or loss of consciousness?'),
 ('Has there been a traumatic injury or accident that requires urgent medical attention?'),
 ('Are you or someone else experiencing symptoms of a stroke, such as sudden numbness, weakness, or difficulty speaking?'),
 ('Have you or someone else ingested a poisonous substance or overdosed on medication?'),
 ('Are you or someone else experiencing severe allergic reactions, such as difficulty breathing or swelling of the throat?'),
 ('Have you or someone else experienced sudden cardiac arrest or stopped breathing?'),
 ('Are you or someone else in imminent danger or need of immediate assistance?');

INSERT INTO triage2_questions (question_text, default_value) VALUES
('Are you experiencing confusion, disorientation, or difficulty understanding your surroundings?'),
('Do you feel extremely tired, weak, or lacking energy?', 'No'),
('Are you experiencing severe pain or discomfort that requires urgent attention?'),
('Have you recently experienced a high-risk event or situation, such as a fall, injury, or sudden onset of symptoms?'),
('Do you have a history of medical conditions or treatments that could increase your risk for complications or require urgent attention?');
    

INSERT INTO appointment_questions (question_text) VALUES
('Will your appointment involve the use of multiple specific medical equipment or devices?'),
('Will your appointment include complex or multiple special procedures or treatments?'),
('Will your appointment require coordinated care from multiple specialized healthcare professionals or specialists?');

INSERT INTO appointment_options (question_id, option_option,option_text) VALUES
(1, 'None','None'),
(1, 'Yes Multiple', 'Yes, multiple specific medical equipment or devices'),
(1, 'Yes But Just One','Yes, but just one specific medical equipment or device'),
(2, 'None','None'),
(2, 'Yes Multiple','Yes, complex or multiple special procedures or treatments'),
(2, 'Yes But Just One','Yes, but just one special procedure or treatment'),
(3, 'None','None'),
(3, 'Yes Multiple','Yes, coordinated care from multiple specialized healthcare professionals or specialists'),
(3, 'Yes But Just One','Yes, but just one specialized healthcare professional or specialist');
          
          ''')