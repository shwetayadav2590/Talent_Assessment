# Exam Management System(Quizify…)
This is an Exam Management System built using Flask for creating and managing exams. It allows users to log in, register, generate question papers, submit and assess exams, and view assessment reports.

## Table of Contents
1. Description
2. Getting Started
3. Prerequisites
4. Installation
5.Configuration
6. Database Setup
7. Usage
8. Roles and Responsibilities
9. Features
10. Contributing

### Description

The Exam Management System provides the following functionalities:

User registration and login.
Role-based access control (SME, Examiner, Student, Question Manager).
Uploading CSV files to create and manage question banks.
Generating question papers for exams.
Submitting exams and calculating scores.
Viewing assessment reports.

## Getting Started

### Prerequisites
Before you begin, ensure you have the following software installed:

Python (version 3.6 or higher)
pip (Python package manager)

### Installation
Clone the repository:

bash
git clone https://github.com/your_username/your_project.git

Navigate to the project directory:

bash
cd your_project

Install the required packages using the provided requirements.txt:

bash
pip install -r requirements.txt

### Configuration
Edit the config.py file located in C:\Users\yadav\Downloads\my_project (3).zip\my_project
to set up your main application's database configuration.

Edit the config.py file located in
 C:\Users\yadav\Downloads\my_project (3).zip\my_project\pythonfile\py_files 
to set up your Python files' database configuration.

### Database Setup
Run the SQL queries provided in the “create 8 tables single query(question_bank)” file to create the necessary tables.
Location: C:\Users\yadav\Downloads\my_project (3).zip\my_project\pythonfile

### Usage
Run the Flask application:

bash
python app.py

Access the application in your web browser at http://localhost:5000.

Follow the on-screen instructions to register, log in, and use the various features of the Exam Management System.

### Roles and Responsibilities

1. Question Manager
The Question Manager role is responsible for managing the question bank. Their responsibilities include:

Uploading Input Files: The Question Manager can upload input files in CSV format, which contain questions to be added to the question bank.

2. SME (Subject Matter Expert)
The SME role is responsible for making necessary updates to the question bank and managing exams. Their responsibilities include:

Reviewing and Updating Questions: The SME can review and update existing questions in the question bank to ensure accuracy and relevance.
Generating Question Papers: The SME can generate question papers for exams, selecting the subject and the number of questions.

3. Examiner
The Examiner role is responsible for conducting exams and assessing student responses. Their responsibilities include:

Generating Question Papers: Examiners can generate question papers for exams, selecting the subject and the number of questions.
Assessing Student Responses: Examiners can evaluate and score student responses to submitted exams.

4. Student
The Student role is responsible for taking exams and viewing assessment reports. Their responsibilities include:

Taking Exams: Students can select answers for each question and submit exams.
Viewing Assessment Reports: Students can view their assessment reports, which include exam history and scores.

### Features
-- User Registration: New users can register by providing their username, password, email, and phone number.

-- User Login: Registered users can log in using their credentials.

-- CSV Upload: SMEs and Question Managers can upload CSV files containing questions to create and manage question banks.

-- Generate Question Paper: SMEs and Examiners can generate question papers for exams, selecting the subject and the number of questions.

-- Exam Submission: Students can submit exams, selecting answers for each question.

-- Assessment Report: Students can view their assessment report, which includes exam history and scores.

### Contributing
Contributions are welcome! If you have any improvements or new features to suggest, please fork the repository and create a pull request.

Fork the repository.
Create a new branch: git checkout -b feature-name
Make your changes and commit them: git commit -m 'Add some feature'
Push to the branch: git push origin feature-name
Create a pull request.
