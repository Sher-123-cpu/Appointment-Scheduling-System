from Controllers.EmailSender import EmailSender
from Controllers.UserController import UserController
from datetime import datetime


class NotificationController:

    
    def send_incoming_patient_notification(patient_id,LocationName, appointment, location_email, triage_level):
        # Construct email subject
        subject = f"Urgent Assistance Needed: Incoming Patient at {LocationName}"

        appointment_time = datetime.strptime(str(appointment['AppointmentTime']), '%H:%M:%S').strftime('%I:%M %p')
        

        first_name = UserController.get_user(patient_id)[3]
        last_name = UserController.get_user(patient_id)[4]
        patient_name = first_name + ' ' + last_name


        # Construct email body
        body = f"Dear Healthcare Team at {LocationName},\n\nAn incoming patient is expected to arrive and requires urgent assistance.\n\n"
        body += f"Patient Name: {patient_name}\n"
        body += f"Triage Level: {triage_level}\n"
        body += f"An appointment has been created for the patient for {appointment_time}.\n\n"
        body += "Please prepare to attend to the patient promptly upon arrival.\n\n"
        body += "If you have any questions or concerns, please feel free to contact us.\n\nBest regards,\nThe Healthcare Team"

        # Send email
        email_sender = EmailSender()
        email_sender.send_email(subject, body, None, location_email)

    def send_account_creation_notification(patient_id):
        # Get user's email address
        receiver_email = UserController.get_patient(patient_id)[4]

        # Get user's first name
        first_name = UserController.get_user(patient_id)[3]


        # Construct email subject
        subject = "Welcome to Our Healthcare System!"

        # Construct email body
        body = f"Dear {first_name},\n\nWelcome to our healthcare system! We're thrilled to have you as a new member.\n\nThank you for creating an account with us. If you have any questions or need assistance, feel free to reach out to us.\n\nBest regards,\nThe Healthcare Team"

        # Send email
        email_sender = EmailSender()
        email_sender.send_email(subject, body, None, receiver_email)


    def send_reschedule_notification(patient_id, appointment, old_appt):
    # Get patient's email address
        receiver_email = UserController.get_patient(patient_id)[4]

        FirstName = UserController.get_user(patient_id)[3]



        # Extract physician's name from old and new appointments
        old_physician = old_appt['Provider']
        new_physician = appointment['Provider']

        appointment_time = datetime.strptime(str(appointment['AppointmentTime']), '%H:%M:%S').strftime('%I:%M %p')
        appointment_date = datetime.strptime(str(appointment['AppointmentDate']), '%Y-%m-%d').strftime('%B %d, %Y')
        appointment['AppointmentTime'] = appointment_time
        appointment['AppointmentDate'] = appointment_date

        old_appointment_time = datetime.strptime(str(old_appt['AppointmentTime']), '%H:%M:%S').strftime('%I:%M %p')
        old_appointment_date = datetime.strptime(str(old_appt['AppointmentDate']), '%Y-%m-%d').strftime('%B %d, %Y')
        old_appt['AppointmentTime'] = old_appointment_time
        old_appt['AppointmentDate'] = old_appointment_date


        # Construct email subject
        subject = "Appointment Rescheduled"

        # Construct email body
        body = f"Dear {FirstName},\n\nYour appointment with {old_physician} scheduled for {old_appt['AppointmentDate']} at {old_appt['AppointmentTime']} has been rescheduled.\n\nNew appointment details:\nDate: {appointment['AppointmentDate']}\nTime: {appointment['AppointmentTime']}\nLocation: {appointment['AppointmentLocation']}\nPhysician: {new_physician}\n\nIf you have any questions or concerns, please feel free to contact us.\n\nBest regards,\nThe Healthcare Team"

        # Send email
        email_sender = EmailSender()
        email_sender.send_email(subject, body, None, receiver_email)

    def send_schedule_notification(patient_id, appointment):
        # Get patient's email address
        receiver_email = UserController.get_patient(patient_id)[4]
        FirstName = UserController.get_user(patient_id)[3]
        appointment_time = datetime.strptime(str(appointment['AppointmentTime']), '%H:%M:%S').strftime('%I:%M %p')
        appointment_date = datetime.strptime(str(appointment['AppointmentDate']), '%Y-%m-%d').strftime('%B %d, %Y')
        appointment['AppointmentTime'] = appointment_time
        appointment['AppointmentDate'] = appointment_date


        # Extract physician's name from the appointment
        physician_name = appointment['Provider']

        # Construct email subject
        subject = "Appointment Scheduled"

        # Construct email body
        body = f"Dear {FirstName},\n\nYour appointment with {physician_name} has been scheduled.\n\nAppointment details:\n \nDate: {appointment['AppointmentDate']}\nTime: {appointment['AppointmentTime']}\nLocation: {appointment['AppointmentLocation']}\n\nIf you have any questions or concerns, please feel free to contact us.\n\nBest regards,\nThe Healthcare Team"

        # Send email
        email_sender = EmailSender()
        email_sender.send_email(subject, body, None, receiver_email)


    def send_reminder_notification(patient_id, appointment):
        # Get patient's email address
        receiver_email = UserController.get_patient(patient_id)[4]

        # Extract physician's name from the appointment
        physician_name = appointment['Provider']
        appointment_time = datetime.strptime(str(appointment['AppointmentTime']), '%H:%M:%S').strftime('%I:%M %p')
        appointment_date = datetime.strptime(str(appointment['AppointmentDate']), '%Y-%m-%d').strftime('%B %d, %Y')
        appointment['AppointmentTime'] = appointment_time
        appointment['AppointmentDate'] = appointment_date

        # Construct email subject
        subject = "Reminder: Upcoming Appointment"

        # Construct email body
        body = f"Dear Patient,\n\nThis is a reminder for your upcoming appointment with {physician_name}:\n\nAppointment details:\nDate: {appointment['AppointmentDate']}\nTime: {appointment['AppointmentTime']}\nLocation: {appointment['AppointmentLocation']}\n\nPlease make sure to attend your appointment on time.\n\nIf you have any questions or concerns, please feel free to contact us.\n\nBest regards,\nThe Healthcare Team"

        # Send email
        email_sender = EmailSender()
        email_sender.send_email(subject, body, None, receiver_email)

   
    @staticmethod
    def send_tomorrow_appointment_notification(patient_id, appointment):
        # Get patient's email address
        receiver_email = UserController.get_patient(patient_id)[4]

        # Extract appointment details
        a_time = appointment['AppointmentDatetime']
        # Determine the time of day
        time_of_day = NotificationController.determine_time_of_day(a_time)

        appointment_time = datetime.strptime(str(appointment['AppointmentTime']), '%H:%M:%S').strftime('%I:%M %p')
        appointment_date = datetime.strptime(str(appointment['AppointmentDate']), '%Y-%m-%d').strftime('%B %d, %Y')
        appointment['AppointmentTime'] = appointment_time
        appointment['AppointmentDate'] = appointment_date

        # Construct email subject
        subject = "Reminder: Tomorrow's Appointment"
        body = f"Dear Patient,\n\nThis is a reminder that you have an appointment scheduled for Tomorrow {time_of_day}.\n\nAppointment details:\nDate: {appointment_date}\nTime: {appointment_time}\n\nPlease make sure to attend your appointment on time.\n\nIf you have any questions or concerns, please feel free to contact us.\n\nBest regards,\nThe Healthcare Team"
        # Construct email body
        # Send email
        email_sender = EmailSender()
        email_sender.send_email(subject, body, None, receiver_email)

    @staticmethod
    def determine_time_of_day(appointment_time):
        # Determine the time of day based on appointment time
        appointment_hour = appointment_time.hour

        if 7 <= appointment_hour < 12:
            return "Morning"
        elif 12 <= appointment_hour < 17:
            return "Afternoon"
        else:
            return "Evening"


    def send_cancel_notification(patient_id, appointment):
        receiver_email = UserController.get_patient(patient_id)[4]
        FirstName = UserController.get_user(patient_id)[3]
        appointment_time = datetime.strptime(str(appointment['AppointmentTime']), '%H:%M:%S').strftime('%I:%M %p')
        appointment_date = datetime.strptime(str(appointment['AppointmentDate']), '%Y-%m-%d').strftime('%B %d, %Y')
        appointment['AppointmentTime'] = appointment_time
        appointment['AppointmentDate'] = appointment_date


        # Extract physician's name from the appointment
        physician_name = appointment['Provider']

        # Construct email subject
        subject = "Appointment Scheduled"

        # Construct email body
        body = f"Dear {FirstName},\n\nYour appointment with {physician_name} has been cancelled.\n\nAppointment details:\n \nDate: {appointment['AppointmentDate']}\nTime: {appointment['AppointmentTime']}\nLocation: {appointment['AppointmentLocation']}\n\nIf you did not initiate this cancellation or have any questions or concerns, please feel free to contact us.\n\nBest regards,\nThe Healthcare Team"

        # Send email
        email_sender = EmailSender()
        email_sender.send_email(subject, body, None, receiver_email)

    
    def send_feedback_received_notification(patient_id, appointment):
        # Get patient's email address
        receiver_email = UserController.get_patient(patient_id)[4]

        # Extract physician's name from the appointment
        physician_name = appointment['Provider']

        # Extract date and time from the appointment
        appointment_time = datetime.strptime(str(appointment['AppointmentTime']), '%H:%M:%S').strftime('%I:%M %p')
        appointment_date = datetime.strptime(str(appointment['AppointmentDate']), '%Y-%m-%d').strftime('%B %d, %Y')

        # Construct email subject
        subject = "Feedback Received"

        # Construct email body
        body = f"Dear Patient,\n\nThank you for providing your feedback on your recent appointment with {physician_name}.\n\nAppointment Details:\nDate: {appointment_date}\nTime: {appointment_time}\n\nWe appreciate your input and strive to improve our services based on your feedback.\n\nIf you have any further comments or concerns, please feel free to reach out to us.\n\nBest regards,\nThe Healthcare Team"

        # Send email
        email_sender = EmailSender()
        email_sender.send_email(subject, body, None, receiver_email)
