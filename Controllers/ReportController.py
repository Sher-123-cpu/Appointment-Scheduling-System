from.DbController import DbController
import json
from datetime import date
from flask import jsonify

class ReportController:
    @staticmethod
    def generate_and_insert_report(report_type):
        try:
            connection = DbController.get_connection()
            cursor = connection.cursor(dictionary=True)

            # Determine query based on report_type
            query = {
                'appointment_counts': """
                    SELECT AppointmentType, AppointmentStatus, COUNT(*) AS Count
                    FROM Appointment
                    GROUP BY AppointmentType, AppointmentStatus;
                """,
                'patient_demographics': """
                    SELECT 
                        Gender,
                        CASE 
                            WHEN TIMESTAMPDIFF(YEAR, DateOfBirth, CURDATE()) < 18 THEN 'Under 18'
                            WHEN TIMESTAMPDIFF(YEAR, DateOfBirth, CURDATE()) BETWEEN 18 AND 35 THEN '18-35'
                            WHEN TIMESTAMPDIFF(YEAR, DateOfBirth, CURDATE()) BETWEEN 36 AND 55 THEN '36-55'
                            ELSE '55+'
                        END AS AgeGroup,
                        COUNT(*) AS Count
                    FROM Patient
                    GROUP BY Gender, AgeGroup;
                """,
                'appointment_location_counts': """
                    SELECT AppointmentLocation, COUNT(*) AS Count
                    FROM Appointment
                    GROUP BY AppointmentLocation;
                """,
                'appointment_provider_counts': """
                    SELECT Provider, COUNT(*) AS Count
                    FROM Appointment
                    GROUP BY Provider;
                """
            }.get(report_type)

            if not query:
                print ("error: ", "Invalid report type")

            # Execute the query
            cursor.execute(query)
            results = cursor.fetchall()

            # Insert report data into Reports table
            report_data_json = json.dumps(results)
            report_date = date.today()
            query_insert = """
                INSERT INTO Reports (report_type, report_date, report_data)
                VALUES (%s, %s, %s);
            """
            cursor.execute(query_insert, (report_type, report_date, report_data_json))
            connection.commit()

            print( "message: ", "Report generated and inserted successfully.")

        except Exception as e:
            print("error: ", str(e))
        finally:
            connection.close()        

    @staticmethod
    def get_reports(report_type=None):  # Optional filters
            try:
                connection = DbController.get_connection()
                cursor = connection.cursor(dictionary=True)

                query = "SELECT * FROM Reports"
                conditions = []
                values = []

                if report_type:
                    conditions.append("report_type = %s")
                    values.append(report_type)

                if conditions:
                    query += " WHERE " + " AND ".join(conditions)
                
                query += " ORDER BY report_id DESC LIMIT 1"

                cursor.execute(query, values)
                reports = cursor.fetchone()
                return reports
            except Exception as e:
                return jsonify({"error": str(e)}), 500
            finally:
                connection.close()