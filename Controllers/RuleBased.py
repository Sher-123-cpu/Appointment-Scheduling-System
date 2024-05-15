
from datetime import datetime, timedelta

from.DbController import DbController
from.PrefController import PrefController
from.AppController import AppController
from.NotificationController import NotificationController

class RuleBased:
    def soonest_lesser_appt(priority_level):
        """Finds the soonest available appointment with a priority level less than the given level."""
        
        connection = DbController.get_connection()  # Get a database connection
        cursor = connection.cursor(dictionary=True)
        try:
                query = """
                    SELECT * FROM Appointment 
                    WHERE AppointmentTime > NOW() 
                    AND AppointmentStatus = 'Scheduled'
                    AND PriorityLevel > %s
                    ORDER BY AppointmentTime ASC
                    LIMIT 1;
                """
                cursor.execute(query, (priority_level,))
                result = cursor.fetchone()
                return result
        finally:
            connection.close()
            
            
    def soonest_available_appt():
        """Finds the soonest available appointment (any type)."""
        connection = DbController.get_connection()  # Get a database connection
        cursor = connection.cursor(dictionary=True)
        try:
                query = """
                    SELECT * FROM Appointment 
                    WHERE AppointmentTime > NOW() 
                    AND AppointmentStatus = 'Open'
                    ORDER BY AppointmentTime ASC
                    LIMIT 1;
                """
                cursor.execute(query)
                result = cursor.fetchone()
                return result
        finally:
            connection.close()
            

    def soonest_appt(appt_list):
        #if len(appt_list)>0:
            return min(appt_list, key=lambda x: x['AppointmentTime'])
    
    def getApp(app_id):
        connection = DbController.get_connection()  # Get a database connection
        cursor = connection.cursor(dictionary=True)
        
        try:
                query = "SELECT * FROM Appointment WHERE AppointmentID = %s"
                cursor.execute(query, (app_id,))
                result = cursor.fetchone()
                return result
        finally:
            connection.close()
            
    
    
    def find_best(appointment_list):
    

        # Find the highest rank among the appointments
        highest_rank = max(pair[1] for pair in appointment_list)

        # Filter for appointments with the highest rank
        highest_ranked_appointments = [pair[0] for pair in appointment_list if pair[1] == highest_rank]

        # If there's only one, return it; otherwise, find the soonest
    
        return highest_ranked_appointments[0]
       
        
    def create_appointment(patient_id, closest_location, priority_level, minutes):
        """Creates a new appointment slot and schedules it for the patient."""

        # Calculate the appointment time
        appointment_time = datetime.now() + timedelta(minutes=minutes)

        connection = DbController.get_connection()  # Get connection outside of try block
        cursor = connection.cursor(dictionary=True)

        try:
                # Check if an open slot exists within the timeframe
                check_query = """
                    SELECT AppointmentID FROM Appointment
                    WHERE AppointmentTime BETWEEN %s AND DATE_ADD(%s, INTERVAL 1 MINUTE)  -- 1-minute buffer
                    AND AppointmentStatus = 'Open'
                    AND AppointmentLocation = %s  
                    LIMIT 1;
                """
                cursor.execute(check_query, (appointment_time, appointment_time, closest_location))
                existing_appointment = cursor.fetchone()

                if existing_appointment:
                    # Use the existing open slot
                    appointment_id = existing_appointment["AppointmentID"]
                    AppController.ScheduleAppointment(appointment_id, priority_level, 'In-Person', patient_id, 'Scheduled')
                    return RuleBased.getApp(appointment_id)
                else:
                    appointment_id = AppController.generate_appointment_id()
                    pref = PrefController.get_preference(patient_id)
                    doctor = pref['Provider']
                    # Create a new slot
                    insert_query = """
                        INSERT INTO Appointment (AppointmentID, PriorityLevel, AppointmentTime, AppointmentLocation, AppointmentType, AppointmentStatus, UserID, Provider)
                        VALUES (%s, %s, %s, %s, 'In-Person', 'Open', %s, %s); 
                    """
                    cursor.execute(insert_query, (appointment_id,priority_level, appointment_time, closest_location,patient_id,doctor))
                    connection.commit()
                     # Get the ID of the new appointment

                # Schedule the appointment for the patient
                AppController.ScheduleAppointment(appointment_id, priority_level, 'In-Person', patient_id, 'Scheduled')

                # Fetch and return the newly scheduled appointment
                new_appointment = RuleBased.getApp(appointment_id)
                return new_appointment

        finally:
            connection.close()
            
    def reschedule_appointment(patient_id, preferences, priority_level, closest_location,old_appt):
        """Reschedules an appointment by finding a new one and notifying the patient."""
        if priority_level < 3:
             appointment = RuleBased.Urgent_Appointment(patient_id,priority_level,closest_location)
        elif priority_level == 3:
            soonest_available=  RuleBased.soonest_available_appt() 
            AppController.ScheduleAppointment(soonest_available['AppointmentID'], priority_level,'In-Person', patient_id,'Scheduled')
            appointment = RuleBased.getApp(soonest_available['AppointmentID'])
           
        else:
            appointment =  RuleBased.NonCritical_Appointment(patient_id, preferences,priority_level)
        
        old = AppController.get_appointment_details(old_appt['AppointmentID'])
        new = AppController.get_appointment_details(appointment['AppointmentID'])

        NotificationController.send_reschedule_notification(patient_id,new,old)

        # Fetch the existing appointment to get its details
         
    def Urgent_Appointment(patient_id,priority_level,closest_location):
        if priority_level == 1:
            minutes = 10
        else: 
            minutes = 30
        soonest_less_important = RuleBased.soonest_lesser_appt(priority_level) 
        if soonest_less_important == None:
            soonest_less_important = RuleBased.soonest_available_appt() 
      
        soonest_available=  RuleBased.soonest_available_appt() 
       

        sooner = RuleBased.soonest_appt([soonest_less_important,soonest_available])
        if RuleBased.is_within_n_minutes_away(sooner['AppointmentTime'],minutes) and sooner['AppointmentLocation'] == closest_location:
            AppController.OpenAppointment(sooner['AppointmentID'],'Open')
            AppController.ScheduleAppointment(sooner['AppointmentID'], priority_level,'In-Person', patient_id,'Scheduled')
            newAppointment =RuleBased.getApp(sooner['AppointmentID'])
            if sooner['PriorityLevel'] != 0:
                newuserpref = PrefController.get_preference(sooner['UserID'])
                RuleBased.reschedule_appointment(sooner['UserID'],newuserpref,sooner['PriorityLevel'],sooner['AppointmentLocation'],sooner)
        else:      
            newAppointment =  RuleBased.create_appointment(patient_id,closest_location,priority_level,minutes)
        return newAppointment

    @staticmethod
    def schedule_appointment(patient_id, preferences,priority_level,closest_location):

        if priority_level < 3:
             return RuleBased.Urgent_Appointment(patient_id,priority_level,closest_location)
        elif priority_level == 3:
            soonest_available=  RuleBased.soonest_available_appt() 
            AppController.ScheduleAppointment(soonest_available['AppointmentID'], priority_level,PrefController.get_preference(patient_id)['Type'], patient_id,'Scheduled')
            newAppointment =RuleBased.getApp(soonest_available['AppointmentID'])
            return newAppointment
        else:
            return RuleBased.NonCritical_Appointment(patient_id, preferences,priority_level)
        

        
    def NonCritical_Appointment(patient_id, preferences,priority_level):
    
        available_appointments =  RuleBased.query_available_appointments() 
        preference_levels = PrefController.getPrefRank(patient_id) 

        
        pref_dict = {}
        pref_dict['Location'] = [preferences['Location'],preference_levels['Location_rank']]
        pref_dict['Provider'] = [preferences['Provider'],preference_levels['Provider_rank']]
        pref_dict['TimeOfDay'] = [preferences['TimeOfDay'],preference_levels['TimeOfDay_rank']]

        level_ones = []
        level_twos = []
        level_threes = []
        level_fours = []
        level_fives = []
        appointmentrank = []


        

        for pref_key, pref_value in pref_dict.items():
            if int(pref_value[1]) == 1:
                level_ones.append(pref_key)
            elif int(pref_value[1]) == 2:
                level_twos.append(pref_key)
            elif int(pref_value[1]) == 3:
                level_threes.append(pref_key)
            elif int(pref_value[1]) == 4:
                level_fours.append(pref_key)
            elif int(pref_value[1]) == 5:
                level_fives.append(pref_key)
        check = -1

       
        
        if len(level_ones)>0:
            check = RuleBased.check_level(level_ones, available_appointments,appointmentrank,priority_level,patient_id,pref_dict,preferences)
            if check != -1:
                return check 
        if len(level_twos)>0:
            check = RuleBased.check_level(level_twos, available_appointments,appointmentrank,priority_level,patient_id,pref_dict,preferences)
            if check != -1:
                return check
        if len(level_threes)>0:
            check = RuleBased.check_level(level_threes, available_appointments,appointmentrank,priority_level,patient_id,pref_dict,preferences)
            if check != -1:
                return check
        if len(level_fours)>0:
            check = RuleBased.check_level(level_fours, available_appointments,appointmentrank,priority_level,patient_id,pref_dict,preferences)
            if check != -1:
                return check
        if len(level_fives)>0:
            check = RuleBased.check_level(level_fives, available_appointments,appointmentrank,priority_level,patient_id,pref_dict,preferences)
            if check != -1:
                return check
        appointment = available_appointments[0]
        AppController.ScheduleAppointment(appointment['AppointmentID'], priority_level,preferences['Type'], patient_id,'Scheduled')
        newAppointment = RuleBased.getApp(appointment['AppointmentID'])
        return newAppointment
    

    def check_level(level, available_appointments,appointmentrank,priority_level,patient_id,pref_dict,preferences):
            for appointment in available_appointments:
                counter = 0
                for pref_key in level:
                    if RuleBased.matches_preference(appointment, pref_key,pref_dict):    
                        counter +=1  
                if counter == len(level):
                    AppController.ScheduleAppointment(appointment['AppointmentID'], priority_level,preferences['Type'], patient_id,'Scheduled')
                    newAppointment = RuleBased.getApp(appointment['AppointmentID'])
                    return newAppointment
                
                elif counter > 0:
                    appointmentrank.append((appointment,counter)) 
                
                

            
            if len(appointmentrank) > 1:
                best = RuleBased.find_best(appointmentrank)
                AppController.ScheduleAppointment(best['AppointmentID'], priority_level,PrefController.get_preference(patient_id)['Type'], patient_id,'Scheduled')
                newAppointment = RuleBased.getApp(best['AppointmentID'])
                return newAppointment
            return -1
        
    
    def matches_preference(appointment, pref_key,pref_dict):
        """ Implements rule-based matching logic.
            Rules for matching in this example:

            1. Appointment Type must match.
            2. Provider must match (if the preference has a provider).
            3. Location must match (if the preference has a location).
            4. Time of day must fall within the preferred time range.
            """
        if pref_key == 'Provider':

            if  appointment['Provider'] ==  pref_dict[pref_key][0]:
                
                return True
        
        if pref_key == 'Location':  


            if  appointment['AppointmentLocation'] == pref_dict[pref_key][0]:
                return True
            

        if pref_key == 'TimeOfDay':
            pref_start, pref_end =  RuleBased.get_time_range(pref_dict[pref_key][0])
        
            appt_time = appointment['AppointmentTime'].time() 
            if (pref_start <= appt_time <= pref_end):
                return True

        # No rule matched!
        return False

    def get_time_range(time_of_day):
            import datetime
            """ Helper to map 'Morning', 'Afternoon' etc. to time ranges"""
            if time_of_day == 'Morning':
                return datetime.time(7, 0), datetime.time(11, 59)
            elif time_of_day == 'Afternoon':
                return datetime.time(12, 0), datetime.time(16, 59)
            else:
                return datetime.time(17, 0), datetime.time(22, 0)
            # ... Add more cases

        # Placeholder - You'd implement this with your database library
    def query_available_appointments():
    # Get a database connection
        connection = DbController.get_connection()  # Get a database connection
        cursor = connection.cursor(dictionary=True)

        # Example assuming appointments for the next week with status 'Available'
       

        query = """
            SELECT * FROM Appointment 
            WHERE AppointmentTime > NOW()
            AND AppointmentStatus = 'Open'
            ORDER BY AppointmentTime; 
        """
    
        

        try:
                cursor.execute(query)
                result = cursor.fetchall()
                return result
        finally:
            # Close the database connection
            connection.close()


    def is_within_n_minutes_away(appointment_time,time_minute):
        # Get the current time
        current_time = datetime.now()

        # Calculate the difference between the appointment time and current time
        time_difference = appointment_time - current_time

        # Define a timedelta representing 30 minutes
        t_minutes = timedelta(minutes=time_minute)

        # Check if the time difference is less than 30 minutes
        if time_difference <= t_minutes:
            return True
        else:
            return False