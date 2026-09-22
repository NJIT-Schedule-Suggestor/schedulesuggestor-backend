-- Schedule Suggestor DB schema
-- Reconstructed from usage in dataLoader.py, retrieveCourses.py, generateSchedule.py
-- Run this once against a fresh database (local or RDS) before starting the app.

CREATE DATABASE IF NOT EXISTS schedule_suggestor;
USE schedule_suggestor;

-- Raw landing table: one row per (course, section, day) meeting,
-- loaded directly from parsed/normalized/*.csv by dataLoader.py
CREATE TABLE IF NOT EXISTS RawCourseMeetings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    Course VARCHAR(20) NOT NULL,
    Section VARCHAR(10) NOT NULL,
    Title VARCHAR(255),
    DeliveryMode VARCHAR(50),
    Credits DECIMAL(3,1),
    Day VARCHAR(20),
    StartTime TIME,
    EndTime TIME
);

-- One row per unique (course_code, section), built by
-- retrieveCourses.py's load_courses_into_schedule_tables()
CREATE TABLE IF NOT EXISTS CourseSections (
    id INT AUTO_INCREMENT PRIMARY KEY,
    course_code VARCHAR(20) NOT NULL,
    section VARCHAR(10) NOT NULL,
    mode VARCHAR(50),
    title VARCHAR(255),
    credits DECIMAL(3,1),
    UNIQUE KEY uq_course_section (course_code, section)
);

-- One row per meeting day for a section, FK back to CourseSections
CREATE TABLE IF NOT EXISTS SectionMeetings (
    id INT AUTO_INCREMENT PRIMARY KEY,
    section_id INT NOT NULL,
    day_of_week VARCHAR(20) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    FOREIGN KEY (section_id) REFERENCES CourseSections(id) ON DELETE CASCADE
);
