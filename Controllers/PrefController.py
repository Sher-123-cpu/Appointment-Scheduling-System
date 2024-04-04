from .DbController import DbController

class PrefController: 
    @staticmethod
    def submit_preferences(user_id, doctor, time, location, preference_type):
        pref_id = PrefController.generate_preference_id()
        
        try:
            conn = DbController.get_connection()
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO Preference (UserID, PreferenceID, Type, Provider, Location, TimeOfDay) 
                            VALUES (%s, %s, %s, %s, %s, %s)''',
                        (user_id, pref_id, preference_type, doctor, location, time))
            conn.commit()  # Commit the transaction
        except Exception as e:
            print(f"Error occurred: {e}")
            conn.rollback()  # Rollback the transaction in case of an error
        finally:
            if conn:
                conn.close()  # Close the connection
                return "Preferences submitted Succesfully"
        

    @staticmethod    
    def generate_preference_id():
        try:
            conn = DbController.get_connection()
            cursor = conn.cursor()
            cursor.execute("SELECT PreferenceID FROM Preference ORDER BY PreferenceID DESC LIMIT 1")
            last_pref_id = cursor.fetchone()
            if last_pref_id:
                last_id_number = int(last_pref_id[0][2:])
                new_pref_id = 'PR{:03d}'.format(last_id_number + 1)
            else:
                new_pref_id = 'PR001'
        except Exception as e:
            print(f"Error occurred: {e}")
            new_pref_id = None
        finally:
            if conn:
                conn.close()  # Close the connection
        return new_pref_id
