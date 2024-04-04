import mysql.connector
from .DbController import DbController

class UserController:
    @staticmethod
    def user_exists(username,password):
        conn = DbController.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM User WHERE Username = %s AND UserPassword = %s", (username,password))
        existing_user = cursor.fetchone()
        conn.close()
        return existing_user
    

    @staticmethod
    def register_user(first_name, last_name, username, password, account_type, gender, dob, phone, email):
        if UserController.user_exists(username,password):
            error_message = "User with this username already exists."
            return [error_message,0]

        user_id = UserController.generate_user_id()
        
        conn = DbController.get_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO User (UserID, Username, UserPassword, FirstName, LastName, AccountType)
                        VALUES (%s, %s, %s, %s, %s, %s)''',
                    (user_id, username, password, first_name, last_name, account_type))
        
        cursor.execute('''INSERT INTO Patient (UserID, Gender, DateOfBirth, PhoneNumber, Email)
                        VALUES (%s, %s, %s, %s, %s)''',
                    (user_id, gender, dob, phone, email))
        
        conn.commit()
        conn.close()
        
        return ["User registered successfully, Please Select Preferences",user_id]

        
    def register_admin(username, password, first_name, last_name, account_type):
        if UserController.user_exists(username,password):
            error_message = "Administrator with this username already exists."
            return error_message

        user_id = UserController.generate_admin_id()
        
        conn = DbController.get_connection()
        cursor = conn.cursor()
        cursor.execute('''INSERT INTO User (UserID, Username, UserPassword, FirstName, LastName, AccountType)
                        VALUES (%s, %s, %s, %s, %s, %s)''',
                    (user_id, username, password, first_name, last_name, account_type))
        
        cursor.execute('''INSERT INTO Administrator (UserID) VALUES (%s)''', (user_id,))
        conn.commit()
        conn.close()
        
        return "Administrator account registered successfully!"


    @staticmethod
    def generate_user_id():
        conn = DbController.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT UserID FROM Patient ORDER BY UserID DESC LIMIT 1")
        last_user_id = cursor.fetchone()
        conn.close()
        if last_user_id:
            last_id_number = int(last_user_id[0][2:])
            new_user_id = 'PA{:03d}'.format(last_id_number + 1)
        else:
            new_user_id = 'PA001'
        return new_user_id
    

    def generate_admin_id():
        conn = DbController.get_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT UserID FROM Administrator ORDER BY UserID DESC LIMIT 1")
        last_user_id = cursor.fetchone()
        conn.close()
        if last_user_id:
            last_id_number = int(last_user_id[0][2:])
            new_user_id = 'AD{:03d}'.format(last_id_number + 1)
        else:
            new_user_id = 'AD001'
        return new_user_id


    def check_credentials(username, password):
        conn = DbController.get_connection()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT * FROM User WHERE Username = %s AND UserPassword = %s", (username, password))
        user = cursor.fetchone()
        if user:
            account_type = user['AccountType']
            return {'account_type': account_type}
        else:
            return False
    def get_fullname(username, password):
        conn = DbController.get_connection()
        cursor = conn.cursor()
        
        cursor.execute("SELECT FirstName, LastName FROM User WHERE Username = %s AND UserPassword = %s", (username, password))
        user_data = cursor.fetchone()
        
        conn.close()
        
        if user_data:
            full_name = user_data[0] + " " + user_data[1]
            return full_name
        else:
            return None