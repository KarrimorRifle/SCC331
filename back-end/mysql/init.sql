-- Database creation
CREATE DATABASE IF NOT EXISTS accounts;
CREATE DATABASE IF NOT EXISTS pico;

-- =============================================
-- Table Structure
-- =============================================
-- Accounts
USE accounts;

CREATE TABLE IF NOT EXISTS users (
  user_id INT AUTO_INCREMENT PRIMARY KEY,
  full_name VARCHAR(100) NOT NULL,
  authority ENUM('Reception', 'Admin') NOT NULL DEFAULT 'Reception',
  pass_hash CHAR(60) NOT NULL COMMENT 'BCrypt hashed',
  email VARCHAR(100) NOT NULL UNIQUE,
  cookie CHAR(64) COMMENT 'Secure session token',
  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
  last_login TIMESTAMP,
  INDEX idx_email (email),
  INDEX idx_cookie (cookie)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

-- pico
USE pico
CREATE TABLE IF NOT EXISTS users (
  picoID INT NOT NULL,
  roomID INT NOT NULL,
  logged_at TIMESTAMP NOT NULL
)

CREATE TABLE IF NOT EXISTS luggage ( -- Consider storing it paired up
  picoID INT NOT NULL,
  roomID INT NOT NULL,
  logged_at TIMESTAMP NOT NULL
)

CREATE TABLE IF NOT EXISTS environment (
  picoID INT NOT NULL,
  roomID INT NOT NULL,
  logged_at TIMESTAMP NOT NULL,
  sound INT NOT NULL,
  light INT NOT NULL,
  temperature INT NOT NULL
)

-- =============================================
-- Microservice-specific Accounts
-- =============================================

-- Account Registration Service (Insert only)
CREATE USER IF NOT EXISTS 'account_registration'@'%' IDENTIFIED WITH 'caching_sha2_password' by 'reg_password';
GRANT INSERT ON accounts.users TO 'account_registration'@'%';
ALTER USER 'account_registration'@'%' WITH MAX_USER_CONNECTIONS 1;
FLUSH PRIVILEGES;


-- Account Cookie Management Service (Update cookie + Read)
CREATE USER IF NOT EXISTS 'cookie_manager'@'%' IDENTIFIED WITH 'caching_sha2_password' by 'cookie_password';
GRANT SELECT, UPDATE(cookie, last_login) ON accounts.users TO 'cookie_manager'@'%';
ALTER USER 'cookie_manager'@'%' WITH MAX_USER_CONNECTIONS 1;
FLUSH PRIVILEGES;

-- Data Processing Service (pico Insert)
CREATE USER IF NOT EXISTS 'data_processor'@'%' IDENTIFIED WITH 'caching_sha2_password' by 'process_password';
GRANT INSERT ON pico.* TO 'data_processor'@'%';
ALTER USER 'data_processor'@'%' WITH MAX_USER_CONNECTIONS 1;
FLUSH PRIVILEGES;

-- Data Reading Service (pico Read)
CREATE USER IF NOT EXISTS 'data_reader'@'%' IDENTIFIED WITH 'caching_sha2_password' by 'read_password';
GRANT SELECT ON pico.* TO 'data_reader'@'%';
ALTER USER 'data_reader'@'%' WITH MAX_USER_CONNECTIONS 1;
FLUSH PRIVILEGES;

-- Data Deletion Service (pico Delete + Read)
CREATE USER IF NOT EXISTS 'data_admin'@'%' IDENTIFIED WITH 'caching_sha2_password' by 'admin_password';
GRANT SELECT, DELETE ON pico.* TO 'data_admin'@'%';
ALTER USER 'data_admin'@'%' WITH MAX_USER_CONNECTIONS 1;
FLUSH PRIVILEGES;


-- =============================================
-- Security Hardening
-- =============================================
-- Remove remote root access
DELETE FROM mysql.user WHERE User='root' AND Host NOT IN ('localhost', '127.0.0.1', '::1');

-- Remove anonymous users
DELETE FROM mysql.user WHERE User='';

-- Remove test database
DROP DATABASE IF EXISTS test;

-- Apply privileges
FLUSH PRIVILEGES;