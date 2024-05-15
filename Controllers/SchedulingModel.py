import schedule
from.AppController import AppController
from.NotificationController import NotificationController
from.ReportController import ReportController
import time
import datetime


class SchedulingModel:
    @staticmethod
    def start():

        schedule.every(60).minutes.do(SchedulingModel.send_reminders)
        schedule.every(25).minutes.do(SchedulingModel.set_completed)
        schedule.every().day.at("22:00").do(SchedulingModel.send_daily_reminders)
        schedule.every().day.at("00:00").do(SchedulingModel.monthly_report)

        while True:
            schedule.run_pending()
            time.sleep(1)


    @staticmethod
    def monthly_report():
        ReportController.generate_and_insert_report('appointment_counts')
        ReportController.generate_and_insert_report('patient_demographics')
        ReportController.generate_and_insert_report('appointment_location_counts')
        ReportController.generate_and_insert_report('appointment_provider_counts')
        print('reports_generated')
    @staticmethod
    def send_reminders():
        upcoming_appointments = AppController.get_upcoming_appointments_reminder()
        current_time = datetime.datetime.now()

        for appointment in upcoming_appointments:
            appointment_datetime = appointment['AppointmentDatetime']
            
            time_difference = appointment_datetime - current_time

            if time_difference <= datetime.timedelta(hours=2):
                patient_id = appointment['UserID']
                NotificationController.send_reminder_notification(patient_id, appointment)
    def set_completed():
        current_time = datetime.datetime.now()
        appointments = AppController.get_appointments()
        for appointment in appointments:
            appointment_datetime = appointment['AppointmentDatetime']
            status = appointment['AppointmentStatus']
            ap_id = appointment['AppointmentID']

            if appointment_datetime < current_time:
                if status == 'Scheduled' :
                    AppController.set_completed(ap_id)
                elif status == 'Open':
                    AppController.cancel_appointment(ap_id)
        

    @staticmethod
    def send_daily_reminders():
        # Get upcoming appointments with priority level > 2
        upcoming_appointments = AppController.get_upcoming_appointments_reminder()

        # Get current time
        current_time = datetime.datetime.now()

        for appointment in upcoming_appointments:
            appointment_datetime = appointment['AppointmentDatetime']
            time_difference = appointment_datetime - current_time

            # Check if the appointment is within 24 hours
            if time_difference <= datetime.timedelta(hours=24) and int(appointment['PriorityLevel'] > 2):
                patient_id = appointment['UserID']
                NotificationController.send_tomorrow_appointment_notification(patient_id, appointment)
