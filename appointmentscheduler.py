import mysql.connector

class RuleBasedAppointmentScheduler:
    def __init__(self, appointments):
        self.appointments = appointments

    def recommend_appointments(self, user_preferences):
        recommended_appointments = []
        for appointment in self.appointments:
            score = self.calculate_score(appointment, user_preferences)
            recommended_appointments.append((appointment, score))
        recommended_appointments.sort(key=lambda x: x[1], reverse=True)
        return [appt for appt, _ in recommended_appointments]

    def calculate_score(self, appointment, user_preferences):
        score = 0
        for preference, weight in user_preferences.items():
            if self.matches_preference(appointment, preference):
                score += weight
        return score

    def matches_preference(self, appointment, preference):
        field, value = preference
        return appointment.get(field) == value

# Establish connection to MySQL database
connection = mysql.connector.connect(
    host="localhost",
    user="Capstone ",
    password="capstonepass",
    database="appointmentscheduler"
)

# Define a function to fetch user preferences from MySQL database
def fetch_user_preferences_from_database():
    cursor = connection.cursor()
    cursor.execute("SELECT field, value, weight FROM preference")
    preferences = {}
    for field, value, weight in cursor:
        preferences[(field, value)] = weight
    cursor.close()
    return preferences

# Example appointments data
appointments = [
    {'doctor': 'Dr. Smith', 'date': '2024-04-15', 'time': 'afternoon', 'location': 'Hospital A'},
    {'doctor': 'Dr. Johnson', 'date': '2024-04-16', 'time': 'evening', 'location': 'Hospital B'},
    {'doctor': 'Dr. Smith', 'date': '2024-04-17', 'time': 'morning', 'location': 'Clinic C'},
]

# Fetch user preferences from MySQL database
user_preferences = fetch_user_preferences_from_database()

# Create a rule-based appointment scheduler
scheduler = RuleBasedAppointmentScheduler(appointments)

# Recommend appointments based on user preferences
recommended_appointments = scheduler.recommend_appointments(user_preferences)

# Print recommended appointments
print("Recommended Appointments:")
for appointment in recommended_appointments:
    print(appointment)

# Close the connection to the database
connection.close()
