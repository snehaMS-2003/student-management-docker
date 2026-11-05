-- Initialization SQL script for Student Management System
-- Automatically executed when the MySQL container starts up for the first time

CREATE DATABASE IF NOT EXISTS student_db;
USE student_db;

CREATE TABLE IF NOT EXISTS students (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(120) NOT NULL UNIQUE,
    phone VARCHAR(20) NOT NULL,
    department VARCHAR(80) NOT NULL,
    gender ENUM('Male', 'Female', 'Other') NOT NULL,
    date_of_birth DATE NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert sample records if table is empty
INSERT INTO students (name, email, phone, department, gender, date_of_birth)
SELECT * FROM (
    SELECT 'Alice Johnson' AS name, 'alice.johnson@university.edu' AS email, '+1-555-0101' AS phone, 'Computer Science' AS department, 'Female' AS gender, '2001-04-15' AS date_of_birth
    UNION ALL
    SELECT 'Bob Smith', 'bob.smith@university.edu', '+1-555-0102', 'Mechanical Engineering', 'Male', '2000-08-22'
    UNION ALL
    SELECT 'Charlie Davis', 'charlie.davis@university.edu', '+1-555-0103', 'Electrical Engineering', 'Male', '2002-01-10'
    UNION ALL
    SELECT 'Diana Prince', 'diana.prince@university.edu', '+1-555-0104', 'Civil Engineering', 'Female', '2001-11-30'
    UNION ALL
    SELECT 'Evan Wright', 'evan.wright@university.edu', '+1-555-0105', 'Computer Science', 'Other', '2000-05-18'
) AS sample_data
WHERE NOT EXISTS (SELECT 1 FROM students LIMIT 1);

