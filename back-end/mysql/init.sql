-- Database creation
CREATE DATABASE IF NOT EXISTS accounts;
CREATE DATABASE IF NOT EXISTS pico;
CREATE DATABASE IF NOT EXISTS assets;
CREATE DATABASE IF NOT EXISTS warning;

-- =============================================
-- Table Structure
-- =============================================
-- Accounts
USE accounts;

CREATE TABLE IF NOT EXISTS users (
	user_id INT AUTO_INCREMENT PRIMARY KEY,
	full_name VARCHAR(100) NOT NULL,
	authority ENUM('Reception', 'Admin', 'Super Admin') NOT NULL DEFAULT 'Reception',
	pass_hash CHAR(60) NOT NULL COMMENT 'BCrypt hashed',
	email VARCHAR(100) NOT NULL UNIQUE,
	cookie CHAR(64) COMMENT 'Secure session token',
	created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	last_login TIMESTAMP,
	INDEX idx_email (email),
	INDEX idx_cookie (cookie)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4;

CREATE TABLE IF NOT EXISTS messages (
	message_id INT AUTO_INCREMENT PRIMARY KEY,
	receiver_id INT,
	sender_id INT,
	left_message VARCHAR(1000),
	time_sent TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
	is_read BOOLEAN DEFAULT 0,
	FOREIGN KEY (receiver_id) REFERENCES accounts.users(user_id) ON DELETE SET NULL,
	FOREIGN KEY (sender_id) REFERENCES accounts.users(user_id) ON DELETE CASCADE
);

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


CREATE TABLE IF NOT EXISTS staff(
  id INT AUTO_INCREMENT PRIMARY KEY,
  picoID VARCHAR(50) NOT NULL,
  roomID VARCHAR(50) NOT NULL,
  logged_at TIMESTAMP NOT NULL
);

CREATE TABLE IF NOT EXISTS guard (
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

CREATE TABLE IF NOT EXISTS presets (
	preset_id INT AUTO_INCREMENT PRIMARY KEY,
	preset_name VARCHAR(255) NOT NULL,
	owner_id INT DEFAULT NULL,
	image_name VARCHAR(255) DEFAULT NULL,
	image_data LONGBLOB DEFAULT NULL,
	FOREIGN KEY (owner_id) REFERENCES accounts.users(user_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS map_blocks (
	id INT AUTO_INCREMENT PRIMARY KEY,
	preset_id INT NOT NULL,
	roomID VARCHAR(50) NOT NULL,
	label VARCHAR(255) DEFAULT NULL,
	`top` INT NOT NULL,
	`left` INT NOT NULL,
	`width` INT NOT NULL,
	`height` INT NOT NULL,
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

-- Ensure there is always an entry with id 1
INSERT INTO default_preset (id, preset_id) VALUES (1, NULL)
ON DUPLICATE KEY UPDATE id = 1;

CREATE TABLE IF NOT EXISTS config (
	id INT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
	domain VARCHAR(50) NOT NULL,
	loginText VARCHAR(250),
	hero_title VARCHAR(250) NOT NULL,
	hero_subtitle VARCHAR(250) NOT NULL,
	image_name VARCHAR(250) NOT NULL,
	image_data LONGBLOB DEFAULT NULL
);

CREATE TABLE IF NOT EXISTS features (
	id INT AUTO_INCREMENT PRIMARY KEY NOT NULL,
	icon VARCHAR(50) NOT NULL,
	title VARCHAR(50) NOT NULL,
	`description` VARCHAR(500) NOT NULL
);

CREATE TABLE IF NOT EXISTS how_it_works (
	step INT PRIMARY KEY NOT NULL,
	title VARCHAR(50) NOT NULL,
	`description` VARCHAR(500) NOT NULL
);

CREATE TABLE IF NOT EXISTS theme_colours (
	id INT PRIMARY KEY DEFAULT 1 CHECK (id = 1),
	primaryDarkBg VARCHAR(20) NOT NULL,
	primaryDarkText VARCHAR(20) NOT NULL,
	primarySecondaryBg VARCHAR(20) NOT NULL,
	primarySecondaryText VARCHAR(20) NOT NULL,
	primaryLightBg VARCHAR(20) NOT NULL,
	primaryLightText VARCHAR(20) NOT NULL,
	accent VARCHAR(20) NOT NULL,
	accentHover VARCHAR(20) NOT NULL
);

-- Insert data into 'config' table only if it's empty
INSERT INTO config (id, domain, loginText, hero_title, hero_subtitle, image_name, image_data)
SELECT 1, 'airport', 'Login to Monitor', 'Newcastle Airport Monitoring', 
       'Ensuring seamless airport operations with real-time monitoring of security, occupancy, and environmental conditions.',
       'newcastle-airport-image.webp',
       FROM_BASE64(LOAD_FILE('/var/lib/mysql-files/base64_airportimg.txt'))  -- updated file pathortimg.txt'))
WHERE NOT EXISTS (SELECT * FROM config);

-- Insert data into 'features' table only if it's empty (bulk insert)
INSERT INTO features (id, icon, title, `description`)
SELECT * FROM (
    SELECT 1 AS id, 'shield' AS icon, 'Security Alerts' AS title, 'Get notified of any security breaches in real-time.' AS `description`
    UNION ALL
    SELECT 2, 'map', 'Live Airport Map', 'Monitor passenger flow and track luggage locations.'
    UNION ALL
    SELECT 3, 'bell', 'Instant Notifications', 'Receive alerts for emergency and unusual activities.'
    UNION ALL
    SELECT 4, 'clock', '24/7 Monitoring', 'Track airport conditions anytime, anywhere.'
) AS tmp
WHERE NOT EXISTS (SELECT * FROM features);

-- Insert data into 'how_it_works' table only if it's empty (bulk insert)
INSERT INTO how_it_works (step, title, `description`)
SELECT * FROM (
    SELECT 1 AS step, 'Login' AS title, 'Access the system securely.' AS `description`
    UNION ALL
    SELECT 2, 'Monitor', 'Track security, environmental data, and passenger flow in real-time.'
    UNION ALL
    SELECT 3, 'Receive Alerts', 'Get instant updates on critical situations.'
) AS tmp
WHERE NOT EXISTS (SELECT * FROM how_it_works);

-- Insert data into 'theme_colours' table only if it's empty
INSERT INTO theme_colours (id, primaryDarkBg, primaryDarkText, primarySecondaryBg, primarySecondaryText, primaryLightBg, primaryLightText, accent, accentHover)
SELECT 1, '#003865', '#003865', 'lightgray', 'lightgray', 'white', 'white', '#FFD700', '#E6C200'
WHERE NOT EXISTS (SELECT * FROM theme_colours);

-- Warning System
USE warning;

CREATE TABLE IF NOT EXISTS rule (
  id INT AUTO_INCREMENT PRIMARY KEY,
  `name` VARCHAR(50) NOT NULL UNIQUE,
  owner_id INT,
  FOREIGN KEY (owner_id) REFERENCES accounts.users(user_id) ON DELETE SET NULL -- if its null it will allow anyone to delete
);

CREATE TABLE IF NOT EXISTS rule_conditions (
  id int AUTO_INCREMENT PRIMARY KEY,
  rule_id INT NOT NULL,
  roomID VARCHAR(50) NOT NULL,
  variable VARCHAR(50) NOT NULL,
  upper_bound FLOAT NOT NULL,
  lower_bound FLOAT NOT NULL,
  FOREIGN KEY (rule_id) REFERENCES warning.rule(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rule_messages (
  id INT AUTO_INCREMENT PRIMARY KEY,
  rule_id INT NOT NULL,
  authority ENUM("admin", "security", "staff", "users", "everyone") NOT NULL, -- Who the message is going to
  title VARCHAR(255) NOT NULL,
  `location` VARCHAR(100),
  severity ENUM("doomed", "danger", "warning", "notification") NOT NULL,
  summary VARCHAR(255),
  FOREIGN KEY (rule_id) REFERENCES warning.rule(id) ON DELETE CASCADE
);


CREATE TABLE IF NOT EXISTS rule_logs_activation (
  id INT AUTO_INCREMENT PRIMARY KEY,
  rule_id INT NOT NULL,
  `time` TIMESTAMP NOT NULL,
  FOREIGN KEY (rule_id) REFERENCES warning.rule(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS rule_logs_variables (
  id INT AUTO_INCREMENT PRIMARY KEY,
  log_id INT NOT NULL,
  variable VARCHAR(100) NOT NULL,
  `value` FLOAT NOT NULL,
  upper_bound FLOAT NOT NULL,
  lower_bound FLOAT NOT NULL,
  FOREIGN KEY (log_id) REFERENCES warning.rule_logs_activation(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS tests (
  id INT AUTO_INCREMENT PRIMARY KEY,
  rule_id INT NOT NULL,
  `status` ENUM("success","failure") NOT NULL DEFAULT "failure",
  mode ENUM("full", "messages") NOT NULL DEFAULT "messages",
  result ENUM("not_done", "conditions_met", "conditions_not_met", "messages_sent") NOT NULL DEFAULT "not_done",
  completed_time TIMESTAMP,
  requested_user INT,
  FOREIGN KEY (rule_id) REFERENCES warning.rule(id) ON DELETE CASCADE,
  FOREIGN KEY (requested_user) REFERENCES accounts.users(user_id) ON DELETE SET NULL
);

CREATE TABLE IF NOT EXISTS updated (
  id INT PRIMARY KEY DEFAULT 1,
  updated BOOLEAN NOT NULL DEFAULT 0
);

INSERT INTO updated (id, updated) VALUES (1, 0)
ON DUPLICATE KEY UPDATE id = 1;

-- =============================================
-- Microservice-specific Accounts
-- =============================================

-- Account Registration Service (Insert only)
CREATE USER IF NOT EXISTS 'account_registration'@'%' IDENTIFIED WITH 'caching_sha2_password' BY 'reg_password';
GRANT INSERT ON accounts.users TO 'account_registration'@'%';
ALTER USER 'account_registration'@'%' WITH MAX_USER_CONNECTIONS 1;
FLUSH PRIVILEGES;

-- Account Messaging Service (Read and Write)
CREATE USER IF NOT EXISTS 'account_messages'@'%' IDENTIFIED WITH 'caching_sha2_password' BY 'message_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON accounts.messages TO 'account_messages'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON accounts.users TO 'account_messages'@'%';
ALTER USER 'account_messages'@'%' WITH MAX_USER_CONNECTIONS 1;
FLUSH PRIVILEGES;

-- Account Cookie Management Service (Update cookie + Read)
CREATE USER IF NOT EXISTS 'cookie_manager'@'%' IDENTIFIED WITH 'caching_sha2_password' BY 'cookie_password';
GRANT SELECT, UPDATE(cookie, last_login) ON accounts.users TO 'cookie_manager'@'%';
ALTER USER 'cookie_manager'@'%' WITH MAX_USER_CONNECTIONS 1;
FLUSH PRIVILEGES;

-- Data Processing Service (pico Insert)
CREATE USER IF NOT EXISTS 'data_processor'@'%' IDENTIFIED WITH 'caching_sha2_password' BY 'process_password';
GRANT INSERT ON pico.* TO 'data_processor'@'%';
ALTER USER 'data_processor'@'%' WITH MAX_USER_CONNECTIONS 1;
FLUSH PRIVILEGES;

-- Data Reading Service (pico Read)
CREATE USER IF NOT EXISTS 'data_reader'@'%' IDENTIFIED WITH 'caching_sha2_password' BY 'read_password';
GRANT SELECT ON pico.* TO 'data_reader'@'%';
ALTER USER 'data_reader'@'%' WITH MAX_USER_CONNECTIONS 1;
FLUSH PRIVILEGES;

-- Data Deletion Service (pico Delete + Read)
CREATE USER IF NOT EXISTS 'data_admin'@'%' IDENTIFIED WITH 'caching_sha2_password' BY 'admin_password';
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

-- warning Editing service
CREATE USER IF NOT EXISTS 'warning_editor'@'%' IDENTIFIED WITH 'caching_sha2_password' BY 'warning_password';
GRANT SELECT, INSERT, UPDATE, DELETE ON warning.rule            TO 'warning_editor'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON warning.rule_conditions TO 'warning_editor'@'%';
GRANT SELECT, INSERT, UPDATE, DELETE ON warning.rule_messages   TO 'warning_editor'@'%';
GRANT SELECT ON warning.rule_logs_activation      TO 'warning_editor'@'%';
GRANT SELECT ON warning.rule_logs_variables       TO 'warning_editor'@'%';
GRANT SELECT, INSERT ON warning.tests             TO 'warning_editor'@'%';
GRANT SELECT ON accounts.users                    TO 'warning_editor'@'%';
GRANT SELECT, UPDATE(updated) ON warning.updated  TO 'warning_editor'@'%';
FLUSH PRIVILEGES;

CREATE USER IF NOT EXISTS 'warning_processor'@'%' IDENTIFIED WITH 'caching_sha2_password' BY 'processor_password';
GRANT SELECT ON warning.rule            TO 'warning_processor'@'%';
GRANT SELECT ON warning.rule_conditions TO 'warning_processor'@'%';
GRANT SELECT ON warning.rule_messages   TO 'warning_processor'@'%';
GRANT SELECT, INSERT, UPDATE ON warning.rule_logs_activation TO 'warning_processor'@'%';
GRANT SELECT, INSERT, UPDATE ON warning.rule_logs_variables  TO 'warning_processor'@'%';
GRANT SELECT, UPDATE ON warning.tests               TO 'warning_processor'@'%';
GRANT SELECT, UPDATE(updated) ON warning.updated    TO 'warning_processor'@'%';
GRANT SELECT ON accounts.users                      TO 'warning_editor'@'%';
FLUSH PRIVILEGES;

CREATE USER IF NOT EXISTS 'dummy'@'%' IDENTIFIED WITH 'caching_sha2_password' BY 'dummy';
GRANT SELECT, INSERT ON pico.* TO 'dummy'@'%';

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