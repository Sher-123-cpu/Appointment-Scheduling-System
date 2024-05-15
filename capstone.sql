    DROP DATABASE IF EXISTS AppointmentScheduler;

    CREATE DATABASE AppointmentScheduler;

    USE AppointmentScheduler;

    CREATE USER 'Capstone'@'localhost' IDENTIFIED BY 'capstonepass';

    GRANT ALL PRIVILEGES ON AppointmentScheduler.* TO 'Capstone'@localhost;

    CREATE TABLE IF NOT EXISTS User (
        UserID VARCHAR(10) PRIMARY KEY,
        Username VARCHAR(255) NOT NULL,
        UserPassword VARCHAR(255) NOT NULL,
        FirstName VARCHAR(255), 
        LastName VARCHAR(255),   
        AccountType VARCHAR(50) NOT NULL
    );

    CREATE TABLE IF NOT EXISTS Administrator (
        UserID VARCHAR(10) PRIMARY KEY,
        FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Patient (
        UserID VARCHAR(10) PRIMARY KEY,
        Gender VARCHAR(10),
        DateOfBirth DATE,
        PhoneNumber VARCHAR(15),
        Email VARCHAR(255),
        FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Location (
        LocationID INT  PRIMARY KEY AUTO_INCREMENT,
        LocationName VARCHAR(225),
        LocationEmail VARCHAR(225)
        );


    CREATE TABLE IF NOT EXISTS Appointment (
        AppointmentID VARCHAR(10) PRIMARY KEY,
        PriorityLevel INT,
        AppointmentTime DATETIME,
        AppointmentLocation VARCHAR(255),
        AppointmentType VARCHAR(255),
        AppointmentStatus VARCHAR(50),
        UserID VARCHAR(10),
        Provider VARCHAR(255),
        FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Preference (
        UserID VARCHAR(10),
        PreferenceID VARCHAR(10) PRIMARY KEY,
        Type VARCHAR(255),
        Provider VARCHAR(255),
        Location VARCHAR(255),
        TimeOfDay VARCHAR(50),
        FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS PreferenceRank (
        UserID VARCHAR(10),
        RankID VARCHAR(10) PRIMARY KEY,
        Type_rank VARCHAR(255),
        Provider_rank VARCHAR(255),
        Location_rank VARCHAR(255),
        TimeOfDay_rank VARCHAR(50),
        FOREIGN KEY (UserID) REFERENCES User(UserID) ON DELETE CASCADE
    );

    CREATE TABLE IF NOT EXISTS Feedback (
        id INT AUTO_INCREMENT PRIMARY KEY,
        AppointmentID VARCHAR(10),
        feedback TEXT,
        FOREIGN KEY (AppointmentID) REFERENCES Appointment(AppointmentID)
    );


    CREATE TABLE IF NOT EXISTS Reports (
        report_id INT AUTO_INCREMENT PRIMARY KEY,
        report_type VARCHAR(100) NOT NULL,  -- Type of report (e.g., 'appointment_counts', 'patient_demographics')
        report_date DATE NOT NULL,          -- Date the report was generated
        report_data JSON NOT NULL,          -- Store report data as JSON
        generated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP -- Timestamp of when the report was created 
    );


CREATE TABLE triage2_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_text VARCHAR(255) NOT NULL,
);

CREATE TABLE emergency_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_text VARCHAR(255) NOT NULL
);

CREATE TABLE appointment_questions (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_text VARCHAR(255) NOT NULL
);

CREATE TABLE appointment_options (
    id INT AUTO_INCREMENT PRIMARY KEY,
    question_id INT NOT NULL,
    option_option VARCHAR(255) NOT NULL,
    option_text VARCHAR(255) NOT NULL,
    FOREIGN KEY (question_id) REFERENCES appointment_questions(id)
);