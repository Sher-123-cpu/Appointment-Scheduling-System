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

CREATE TABLE IF NOT EXISTS Feedback (
    id INT AUTO_INCREMENT PRIMARY KEY,
    AppointmentID VARCHAR(10),
    feedback TEXT,
    FOREIGN KEY (AppointmentID) REFERENCES Appointment(AppointmentID)
);



