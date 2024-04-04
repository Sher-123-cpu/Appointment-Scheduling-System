import mysql.connector

class DbController:
    @staticmethod
    def get_connection():
        return mysql.connector.connect(
            host='localhost',
            user='Capstone',
            password='capstonepass',
            database='AppointmentScheduler'
        )