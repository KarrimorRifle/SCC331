-- Database creation
CREATE DATABASE IF NOT EXISTS accounts;
CREATE DATABASE IF NOT EXISTS pico;
CREATE DATABASE IF NOT EXISTS assets;

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
USE pico;
CREATE TABLE IF NOT EXISTS users (
  id INT AUTO_INCREMENT PRIMARY KEY,
  picoID VARCHAR(50) NOT NULL,
  roomID VARCHAR(50) NOT NULL,
  logged_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS luggage ( -- Consider storing it paired up
  id INT AUTO_INCREMENT PRIMARY KEY,
  picoID VARCHAR(50) NOT NULL,
  roomID VARCHAR(50) NOT NULL,
  logged_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS environment (
  id INT AUTO_INCREMENT PRIMARY KEY,
  picoID VARCHAR(50) NOT NULL,
  roomID VARCHAR(50) NOT NULL,
  logged_at TIMESTAMP NOT NULL,
  sound FLOAT NOT NULL,
  light FLOAT NOT NULL,
  temperature FLOAT NOT NULL,
  IAQ FLOAT NOT NULL,
  pressure FLOAT NOT NULL,
  humidity FLOAT NOT NULL
);

-- Use the assets database
USE assets;

CREATE TABLE IF NOT EXISTS files (
  filename VARCHAR(255) NOT NULL PRIMARY KEY,
  filedata LONGBLOB NOT NULL,
  uploaded_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS presets (
  preset_id INT AUTO_INCREMENT PRIMARY KEY,
  preset_name VARCHAR(255) NOT NULL,
  file_id VARCHAR(255),
  owner_id INT NOT NULL,
  FOREIGN KEY (file_id) REFERENCES files(filename) ON DELETE CASCADE,
  FOREIGN KEY (owner_id) REFERENCES accounts.users(user_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS map_blocks (
  id INT AUTO_INCREMENT PRIMARY KEY,
  preset_id INT NOT NULL,
  roomID VARCHAR(50) NOT NULL,
  label VARCHAR(255) DEFAULT roomID,
  location_top INT NOT NULL,
  location_left INT NOT NULL,
  location_width INT NOT NULL,
  location_height INT NOT NULL,
  colour VARCHAR(10) NOT NULL,
  FOREIGN KEY (preset_id) REFERENCES presets(preset_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS preset_trusted (
  preset_id INT NOT NULL,
  user_id INT NOT NULL,
  PRIMARY KEY (preset_id, user_id),
  FOREIGN KEY (preset_id) REFERENCES presets(preset_id) ON DELETE CASCADE,
  FOREIGN KEY (user_id) REFERENCES accounts.users(user_id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS default_preset (
  id INT PRIMARY KEY DEFAULT 1,
  preset_id INT,
  FOREIGN KEY (preset_id) REFERENCES presets(preset_id) ON DELETE SET NULL
);

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

-- Assets Reading Service (Read only)
CREATE USER IF NOT EXISTS 'assets_reader'@'%' IDENTIFIED WITH 'caching_sha2_password' BY 'read_password';
GRANT SELECT ON assets.* TO 'assets_reader'@'%';
ALTER USER 'assets_reader'@'%' WITH MAX_USER_CONNECTIONS 1;
FLUSH PRIVILEGES;

-- Assets Editing Service (Full permissions)
CREATE USER IF NOT EXISTS 'assets_editor'@'%' IDENTIFIED WITH 'caching_sha2_password' BY 'edit_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON assets.* TO 'assets_editor'@'%';
ALTER USER 'assets_editor'@'%' WITH MAX_USER_CONNECTIONS 1;
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