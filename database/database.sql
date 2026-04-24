-- Create the database if it doesn't exist
CREATE DATABASE IF NOT EXISTS matching;

-- Select the database
USE matching;

-- Create the lawyers table
CREATE TABLE IF NOT EXISTS lawyers (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    specialization VARCHAR(255),
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the clients table
CREATE TABLE IF NOT EXISTS clients (
    id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Create the admins table
CREATE TABLE IF NOT EXISTS admins (
    id INT AUTO_INCREMENT PRIMARY KEY,
    username VARCHAR(255) UNIQUE NOT NULL,
    password VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Insert a default admin (password is 'admin123')
INSERT IGNORE INTO admins (username, password)
VALUES ('admin', 'admin123');

-- Insert a test user (password is 'password123')
INSERT IGNORE INTO lawyers (name, email, password, specialization)
VALUES ('Test Lawyer', 'lawyer@example.com', 'password123', 'Family Law');
