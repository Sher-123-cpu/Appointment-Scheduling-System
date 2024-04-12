from datetime import datetime
from .DbController import DbController

class AppController:
    @staticmethod
    def get_appointments():
        try:
            conn = DbController.get_connection()  # Get a database connection
            cursor = conn.cursor(dictionary=True)
            
            # Execute SQL query to fetch appointment data
            cursor.execute("SELECT AppointmentID, DATE(AppointmentTime) AS AppointmentDate, TIME(AppointmentTime) AS AppointmentTime, AppointmentLocation, UserID, AppointmentStatus FROM Appointment")
            
            # Fetch all appointment records
            appointments = cursor.fetchall()
            
            return appointments
        
        except Exception as e:
            print("Error fetching appointments:", e)
            return None
        
        finally:
            if conn:
                conn.close()  # Close the database connection

    @staticmethod
    def get_appointments_patient():
        try:
            conn = DbController.get_connection()  # Get a database connection
            cursor = conn.cursor(dictionary=True)
            
            # Execute SQL query to fetch appointment data
            cursor.execute("SELECT AppointmentID, DATE(AppointmentTime) AS AppointmentDate, TIME(AppointmentTime) AS AppointmentTime, AppointmentLocation, Provider FROM Appointment WHERE appointmentStatus = 'Open'")
            # Fetch all appointment records
            appointments = cursor.fetchall()
            
            return appointments
        
        except Exception as e:
            print("Error fetching appointments:", e)
            return None
        
        finally:
            if conn:
                conn.close()

    @staticmethod
    def get_user_from_app(appointment_id):
        try:
            conn = DbController.get_connection()  # Get a database connection
            cursor = conn.cursor()
            
            # Execute SQL query to fetch appointment record by appointment ID
            cursor.execute("SELECT UserID FROM Appointment WHERE AppointmentID = %s", (appointment_id,))
            
            # Fetch the appointment record
            appointment_record = cursor.fetchone()
            
            if appointment_record:
                user_id = appointment_record[0]
                if user_id is None:
                    return False
                else:
                    return user_id
            
        
        finally:
            if conn:
                conn.close()  # Close the database connection



    @staticmethod
    def get_appointment_details(appointment_id):
        try:
            conn = DbController.get_connection()  # Get a database connection
            cursor = conn.cursor(dictionary=True)
            
            # Execute SQL query to fetch appointment details
            cursor.execute("SELECT DATE(AppointmentTime) AS AppointmentDate, AppointmentLocation, AppointmentStatus, Provider FROM Appointment WHERE AppointmentID = %s", (appointment_id,))
            
            # Fetch the appointment details
            appointment_details = cursor.fetchone()
            
            return appointment_details
        
        except Exception as e:
            print("Error fetching appointment details:", e)
            return None
        
        finally:
            if conn:
                conn.close()  # Close the database connection

    @staticmethod
    def cancel_appointment(appointment_id):
        try:
            conn = DbController.get_connection()  # Get a database connection
            cursor = conn.cursor()
            
            # Execute SQL query to delete the appointment
            cursor.execute("DELETE FROM Appointment WHERE AppointmentID = %s", (appointment_id,))
            
            # Commit the transaction
            conn.commit()
            
            # Close cursor and connection
            cursor.close()
            conn.close()
            
        except Exception as e:
            print("Error cancelling appointment:", e)

    @staticmethod
    def add_appointment(date, time, location,doctor):
        try:
            conn = DbController.get_connection()  # Get a database connection
            cursor = conn.cursor()

            # Generate appointment ID
            appointment_id = AppController.generate_appointment_id()

            # Execute SQL query to insert the appointment into the database
            cursor.execute('''INSERT INTO Appointment (appointmentID, priorityLevel, appointmentTime, 
                              appointmentLocation, appointmentType, appointmentStatus, userID, Provider) 
                              VALUES (%s, NULL, %s, %s, NULL, 'Open', NULL, %s)''',
                           (appointment_id, f"{date} {time}", location, doctor))

            conn.commit()  # Commit the transaction
            return "Appointment Successfully added"  # Return True on success

        except Exception as e:
            print("Error adding appointment:", e)
            return "Failed to add appointment "  # Return False on failure

        finally:
            if conn:
                conn.close()  # Close the database connection

    @staticmethod
    def generate_appointment_id():
        try:
            conn = DbController.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT appointmentID FROM Appointment ORDER BY appointmentID DESC LIMIT 1")
            last_appointment_id = cursor.fetchone()
            if last_appointment_id:
                last_id_number = int(last_appointment_id[0][2:])
                new_appointment_id = 'AP{:03d}'.format(last_id_number + 1)
            else:
                new_appointment_id = 'AP001'
        except Exception as e:
            print(f"Error occurred: {e}")
            new_appointment_id = None
        finally:
            if conn:
                conn.close()  # Close the connection
        return new_appointment_id


    @staticmethod
    def get_appointment_details_modify(appointment_id):
        try:
            conn = DbController.get_connection()  # Get a database connection
            cursor = conn.cursor(dictionary=True)
            
            # Execute SQL query to fetch appointment details
            cursor.execute("SELECT DATE(AppointmentTime) AS AppointmentDate, TIME(AppointmentTime) AS AppointmentTime, AppointmentLocation, Provider AS Doctor FROM Appointment WHERE AppointmentID = %s", (appointment_id,))
            
            # Fetch the appointment details
            appointment_details = cursor.fetchone()
            
            return appointment_details
        
        except Exception as e:
            print("Error fetching appointment details:", e)
            return None
        
        finally:
            if conn:
                conn.close()  # Close the database connection

    @staticmethod
    def modify_appointment(appointment_id, date, time, location, doctor):
        try:
            conn = DbController.get_connection()
            cursor = conn.cursor()
            
            # Update the appointment details in the database
            cursor.execute("UPDATE Appointment SET AppointmentTime = %s, AppointmentLocation = %s, Provider = %s WHERE AppointmentID = %s", (f"{date} {time}", location, doctor, appointment_id))
            
            # Commit the transaction
            conn.commit()
            
            return True  # Return True if the appointment is successfully modified
            
        except Exception as e:
            print("Error modifying appointment:", e)
            conn.rollback()  # Rollback the transaction in case of an error
            return False  # Return False if there is an error modifying the appointment
            
        finally:
            if conn:
                conn.close()
    
    @staticmethod
    def get_past_appointments(user_id):
        try:
            conn = DbController.get_connection()  # Get a database connection
            cursor = conn.cursor(dictionary=True)

            # Execute SQL query to fetch past appointments
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            query = "SELECT AppointmentID, DATE(AppointmentTime) AS AppointmentDate, TIME(AppointmentTime) AS AppointmentTime, AppointmentLocation, Provider AS Doctor FROM Appointment WHERE UserID = %s AND AppointmentTime < %s"
            cursor.execute(query, (user_id, current_datetime))
            
            # Fetch the past appointments
            past_appointments = cursor.fetchall()

            return past_appointments
        except Exception as e:
            print("Error fetching past appointments:", e)
            return []

    @staticmethod
    def get_upcoming_appointments(user_id):
        try:
            conn = DbController.get_connection()  # Get a database connection
            cursor = conn.cursor(dictionary=True)

            # Execute SQL query to fetch upcoming appointments
            current_datetime = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            query = "SELECT AppointmentID, DATE( AppointmentTime) AS AppointmentDate, TIME(AppointmentTime) AS AppointmentTime, AppointmentLocation, Provider AS Doctor FROM Appointment WHERE UserID = %s AND AppointmentTime >= %s"
            cursor.execute(query, (user_id, current_datetime))
            
            # Fetch the upcoming appointments
            upcoming_appointments = cursor.fetchall()

            return upcoming_appointments
        except Exception as e:
            print("Error fetching upcoming appointments:", e)
            return []
    @staticmethod
    def submitfeedback(appointment_id, feedback):
        try:
            conn = DbController.get_connection()
            cursor = conn.cursor()

            # Insert feedback into the Feedback table
            cursor.execute("INSERT INTO Feedback (AppointmentID, feedback) VALUES (%s, %s)", (appointment_id, feedback))
            conn.commit()

            return "Feedback submitted successfully."
        except Exception as e:
            conn.rollback()
            return appointment_id
        finally:
            conn.close()
    @staticmethod
    def remove_reviewed_appointments(appointments):
        try:
            conn = DbController.get_connection()
            cursor = conn.cursor()

            # Get the list of appointment IDs from the Feedback table
            cursor.execute("SELECT DISTINCT AppointmentID FROM Feedback")
            reviewed_appointments = [row[0] for row in cursor.fetchall()]

            # Remove reviewed appointments from the appointments list
            appointments = [appointment for appointment in appointments if appointment['AppointmentID'] not in reviewed_appointments]

            return appointments
        except Exception as e:
            # Handle exceptions here
            return None
        finally:
            conn.close()
    
    @staticmethod
    def OpenAppointment(old_appointment,status):
        try:
            conn = DbController.get_connection()
            cursor = conn.cursor()
            # Set priority, type, and user id to null for the old appointment
            cursor.execute("UPDATE Appointment SET priorityLevel=NULL, appointmentType=NULL, userID=NULL, appointmentStatus=%s WHERE appointmentID=%s", (status, old_appointment))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print("Error in OpenAppointment:", e)
        finally:
            cursor.close()
            conn.close()

    @staticmethod
    def ScheduleAppointment(appointment_id, priority, appointment_type, user_id,status):
        try:
            conn = DbController.get_connection()
            cursor = conn.cursor()
            # Update the appointment with the new details
            cursor.execute("UPDATE Appointment SET priorityLevel=%s, appointmentType=%s, userID=%s, appointmentStatus=%s WHERE appointmentID=%s" , (priority, appointment_type, user_id, status, appointment_id))
            conn.commit()
        except Exception as e:
            conn.rollback()
            print("Error in ScheduleAppointment:", e)
        finally:
            cursor.close()
            conn.close()