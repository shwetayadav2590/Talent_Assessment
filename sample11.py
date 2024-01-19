from flask import Flask, request, render_template, redirect, url_for, session,jsonify
import os
import mysql.connector
from flask import Flask, render_template, send_file, make_response
import random
from io import BytesIO
from fpdf import FPDF
import time
from config import db_config 
current_exam_id = None


app = Flask(__name__)
app.secret_key = 'your_secret_key_here'

# Configure upload folder
app.config['UPLOAD_FOLDER'] = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'uploads')


@app.route('/')
def splash_screen():
    return render_template('splash_screen.html')

@app.route('/login')
def login_page():
    return render_template('login_1.html')

# Other routes and logic...

@app.route('/login', methods=['POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        try:
            connection = mysql.connector.connect(**db_config)
            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                query = 'SELECT user_id, role FROM users WHERE user_name = %s AND password = %s'
                cursor.execute(query, (username, password))
                result = cursor.fetchone()
                connection.close()

                if result:
                    role = result['role']
                    session['username'] = username
                    session['role'] = role
                    user_id = result['user_id']  # Assuming your user ID column is named 'user_id'
                    session['user_id'] = user_id

                    if role == 'sme':
                        return redirect(url_for('questions'))
                    elif role == 'examiner':
                        return render_template('question_paper.html')
                    elif role != 'student':
                        return render_template('index_fileupload.html')
                    else:
                        return render_template('student_dashboard.html')
                else:
                    return "Invalid username or password."
        
        except mysql.connector.Error as err:
            print("Database Error:", err)  # Debug: Print database error
            return "Error connecting to the database.", 500

@app.route('/registration.html')
def registration_page():
    return render_template('registration.html')

@app.route('/register', methods=['POST'])
def register():
    new_username = request.form['newUsername']
    new_password = request.form['newPassword']
    email_id = request.form['email_id']
    phone_no = request.form['phone_no']
    role = 'student'  # Set the role as "student"

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()
        addUserQuery = 'INSERT INTO users (user_name, password, role, email_id, phone_no) VALUES (%s, %s, %s, %s, %s)'
        cursor.execute(addUserQuery, (new_username, new_password, role, email_id, phone_no))
        connection.commit()
        cursor.close()
        connection.close()
        return "User registered successfully!"
    except mysql.connector.Error as err:
        print('Error inserting user: ', err)
        return "Error connecting to the database.", 500


@app.route('/questions', methods=['GET'])
def questions():
    if 'username' in session and 'role' in session and session['role'] == 'sme':
        try:
            connection = mysql.connector.connect(**db_config)
            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)
                cursor.execute("SELECT * FROM mcq")
                questions = cursor.fetchall()
                connection.close()

                return render_template('questions.html', questions=questions)

        except mysql.connector.Error as err:
            print("Database Error:", err)  # Debug: Print database error
            return render_template('questions.html', message=f"Database error: {err}")

    else:
        return redirect(url_for('login'))

@app.route('/update', methods=['POST'])
def update():
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor()
            question_id = request.form.get('question_id')
            query_parts = []

            for key, value in request.form.items():
                if key != 'question_id':
                    query_parts.append(f"{key} = '{value}'")

            update_query = ", ".join(query_parts)
            query = f"UPDATE mcq SET {update_query} WHERE ques_id = {question_id}"
            print("Update Query:", query)  # Debug: Check the query being executed

            cursor.execute(query)
            connection.commit()  # Commit changes to the database
            connection.close()

            return redirect(url_for('questions'))

    except mysql.connector.Error as err:
        print("Database Error:", err)  # Debug: Print database error
        return render_template('questions.html', message=f"Database error: {err}")

# Define the generate_unique_file_name function
def generate_unique_file_name(folder, filename, extname):
    count = 1
    new_filename = filename + extname
    while os.path.exists(os.path.join(folder, new_filename)):
        new_filename = f"{filename}_{count}{extname}"
        count += 1
    return new_filename

@app.route('/index_fileupload.html')
def index_fileupload_page():
    return render_template('index_fileupload.html')

@app.route('/upload', methods=['POST'])
def upload():
    category = request.form['category']  # Get the category from the form
    file = request.files['file']  # Get the uploaded file
    
    if file:
        category_folder_path = os.path.join(app.config['UPLOAD_FOLDER'], category)

        if not os.path.exists(category_folder_path):
            os.makedirs(category_folder_path)

        original_name, extname = os.path.splitext(file.filename)
        file_name_without_ext = os.path.basename(original_name)
        unique_file_name = generate_unique_file_name(category_folder_path, file_name_without_ext, extname)

        file.save(os.path.join(category_folder_path, unique_file_name))
        return f"File uploaded and saved as {unique_file_name} in category {category} successfully!"
    else:
        return "No file uploaded.", 400

# Other routes...

def generate_exam_id():
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT DISTINCT exam_id FROM question_paper"
    cursor.execute(query)
    exam_ids_array = [row[0] for row in cursor.fetchall()]
    cursor.close()
    connection.close()

    exam_id = random.choice(exam_ids_array)
    print(exam_id)
    return exam_id

def generate_ques_id(exam_id):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT ques_id FROM question_paper WHERE exam_id = %s"
    cursor.execute(query, (exam_id,))
    ques_ids = [row[0] for row in cursor.fetchall()]
    print(ques_ids)
    cursor.close()
    connection.close()
    return ques_ids

# Fetch Questions from Database
def fetch_questions(ques_ids):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT ques_id, questions, option_a, option_b, option_c, option_d FROM mcq WHERE ques_id IN (%s)"
    placeholders = ', '.join(['%s'] * len(ques_ids))
    formatted_query = query % placeholders
    cursor.execute(formatted_query, ques_ids)
    questions = cursor.fetchall()
    cursor.close()
    connection.close()
    return questions

@app.route('/question_paper.html')
def display_question_paper():
    exam_id = generate_exam_id()
    ques_ids = generate_ques_id(exam_id)
    questions = fetch_questions(ques_ids)
    print(ques_ids)  # Print the array of fetched ques_ids (for testing purposes)
    question_data = list(enumerate(questions, start=1))  # Pair each question with its index
    return render_template('question_paper.html', questions=questions, exam_id=exam_id)

@app.route('/generate-new-exam')
def generate_new_exam():
    return display_question_paper()  # Reuse the existing logic to generate a new question paper

@app.route('/fetch-answer-key/<int:exam_id>')
def fetch_answer_key(exam_id):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT q.questions, q.correct_ans, q.description FROM mcq q JOIN question_paper qp ON q.ques_id = qp.ques_id WHERE qp.exam_id = %s"
    cursor.execute(query, (exam_id,))
    answer_key = cursor.fetchall()
    cursor.close()
    connection.close()

    return render_template('answer_key.html', answer_key=answer_key, exam_id=exam_id)

@app.route('/download-answer-key/<int:exam_id>')
def download_answer_key_pdf(exam_id):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT q.questions, q.correct_ans, q.option_a, q.option_b, q.option_c, q.option_d, q.description FROM mcq q JOIN question_paper qp ON q.ques_id = qp.ques_id WHERE qp.exam_id = %s"
    cursor.execute(query, (exam_id,))
    answer_key = cursor.fetchall()
    cursor.close()
    connection.close()

    pdf = FPDF(format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", size=12)

    for index, ans in enumerate(answer_key, start=1):
        question_text = f"Q{index}: {ans[0]}"
        correct_option = ans[1]
        correct_option_text = ans[2 + ord(correct_option) - ord('A')]  # Get option text based on correct answer
        answer_description = ans[6]  # Assuming description is at index 6

        pdf.multi_cell(0, 10, question_text)
        pdf.multi_cell(0, 10, f"Correct Answer: {correct_option} ({correct_option_text})")
        pdf.multi_cell(0, 10, f"Answer Description: {answer_description if answer_description else 'None'}")
        pdf.ln(10)

    pdf_filename = f'answer_key_{exam_id}.pdf'
    pdf.output(pdf_filename)

    response = make_response(open(pdf_filename, 'rb').read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename="{pdf_filename}"'

    return response



# Your other Flask app configuration code

# Define the route to download the question paper PDF
@app.route('/download-question-paper/<int:exam_id>')
def download_question_paper_pdf(exam_id):
    connection = mysql.connector.connect(**db_config)
    cursor = connection.cursor()
    query = "SELECT ques_id, questions, option_a, option_b, option_c, option_d FROM mcq WHERE ques_id IN (SELECT ques_id FROM question_paper WHERE exam_id = %s)"
    cursor.execute(query, (exam_id,))
    questions = cursor.fetchall()
    cursor.close()
    connection.close()

    pdf = FPDF(format='A4')
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_left_margin(15)
    pdf.set_right_margin(15)
    
    pdf.set_line_width(0.5)
    pdf.rect(10, 10, pdf.w - 20, pdf.h - 20)

    pdf.set_font("Arial", size=12)
    
    pdf.cell(0, 10, "Question Paper", ln=True, align='C')
    pdf.ln(10)

    for index, question in enumerate(questions, start=1):
        
        question_text = question[1]
        options = [f"A) {question[2]}", f"B) {question[3]}", f"C) {question[4]}", f"D) {question[5]}"]
        
        pdf.set_font("Arial", 'B', size=12)
        pdf.multi_cell(0, 10, f"Q{index}: {question_text}", align='L')
        
        pdf.set_font("Arial", size=12)
        for option in options:
            pdf.cell(0, 10, option, ln=True)
        pdf.ln(5)

    pdf_filename = f'question_paper_{exam_id}.pdf'
    pdf.output(pdf_filename)

    response = make_response(open(pdf_filename, 'rb').read())
    response.headers['Content-Type'] = 'application/pdf'
    response.headers['Content-Disposition'] = f'inline; filename="{pdf_filename}"'

    return response

@app.route('/student_dashboard', methods=['GET', 'POST'])
def student_dashboard():
    user_name = session.get('username')

    if user_name:
        return render_template('student_dashboard.html', user_name=user_name)
    else:
        return "Unauthorized access."  # Handle unauthorized access
@app.route('/student_mainmenu1.html',methods=['GET'])
def student_mainmenu_page():
    return render_template('student_mainmenu1.html')

@app.route('/generate_exam', methods=['GET'])
def generate_exam():
    try:
        selected_subject = request.args.get('subject')
        total_questions = int(request.args.get('totalQuestions'))

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # Generate a unique exam ID for this session
        current_exam_id = generate_unique_exam_id(cursor)

        # Query to fetch random questions from the database for the selected subject
        query = 'SELECT ques_id, questions, option_a, option_b, option_c, option_d, correct_ans FROM mcq WHERE sub_id IN (SELECT sub_id FROM subject WHERE sub_name = %s) ORDER BY RAND() LIMIT %s'
        cursor.execute(query, (selected_subject, total_questions))
        result = cursor.fetchall()

        if not result:
            return jsonify(error='No questions found for the selected subject.')

        # Process the result and format the questions and options
        questions = []
        for row in result:
            ques_id, question, option_a, option_b, option_c, option_d, correct_ans = row
            question_data = {
                'ques_id': ques_id,
                'question': question,
                'option_a': option_a,
                'option_b': option_b,
                'option_c': option_c,
                'option_d': option_d,
                'correct_ans': correct_ans,
                'marks': 4,
            }
            questions.append(question_data)

        # Store the exam data in the question_paper1 table
        for question in questions:
            ques_id = question['ques_id']
            marks = question['marks']
            query = "INSERT INTO question_paper1 (exam_id, ques_id, total_marks) VALUES (%s, %s, %s)"
            cursor.execute(query, (current_exam_id, ques_id, marks))

        connection.commit()
        connection.close()

        # Store the generated exam ID in the session
        session['current_exam_id'] = current_exam_id

        return jsonify(questions)

    except mysql.connector.Error as err:
        print("Database Error:", err)
        return jsonify(error='Error fetching data from the database'), 500


def generate_unique_exam_id(cursor):
    while True:
        exam_id = random.randint(1000, 9999)  # Generate a random 4-digit exam_id
        # Check if the generated exam_id already exists in the database
        query = "SELECT COUNT(*) FROM question_paper1 WHERE exam_id = %s"
        cursor.execute(query, (exam_id,))
        count = cursor.fetchone()[0]
        if count == 0:  # If exam_id is not in use, return it
            return exam_id



@app.route('/submit_exam', methods=['POST'])
def submit_exam():
    try:
        # Get data from the POST request
        user_id = session.get('user_id')
        user_responses = request.json['user_responses']

        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        total_score = 0

        # Get the exam ID from the session
        current_exam_id = session.get('current_exam_id')

        if current_exam_id is None:
            return jsonify(error='No exam ID found in the session'), 400

        # Store user responses in the user_response table and calculate total score
        for response in user_responses:
            ques_id = response['ques_id']
            selected_answer = response['selected_answer']

            cursor.execute("SELECT correct_ans FROM mcq WHERE ques_id = %s", (ques_id,))
            correct_answer = cursor.fetchone()[0]

            score = 4 if selected_answer == correct_answer else 0
            total_score += score

            query = """
                INSERT INTO user_response (user_id, ques_id, answer, score, submission_time, exam_id)
                VALUES (%s, %s, %s, %s, NOW(), %s)
            """
            cursor.execute(query, (user_id, ques_id, selected_answer, score, current_exam_id))

        connection.commit()
        connection.close()

        return jsonify(message='Exam submitted successfully', total_score=total_score)

    except mysql.connector.Error as err:
        print("Database Error:", err)
        return jsonify(error='Error submitting exam'), 500



# Example routes you provided

@app.route('/student2_index.html')
def student2_index_page():
    return render_template('student2_index.html')

@app.route('/submission_complete.html')
def submission_complete_page():
    return render_template('submission_complete1.html')

@app.route('/assessment_report')
def assessment_report_page():
    if 'user_id' in session:
        user_id = session['user_id']

        try:
            connection = mysql.connector.connect(**db_config)
            if connection.is_connected():
                cursor = connection.cursor(dictionary=True)

                # Fetch user details
                user_query = 'SELECT profile_picture, user_name FROM users WHERE user_id = %s'
                cursor.execute(user_query, (user_id,))
                user_result = cursor.fetchone()

                # Fetch exam history with exam_id
                exam_history_query = '''
                    SELECT DISTINCT DATE(submission_time) AS exam_date, COUNT(*) AS total_attempts, exam_id
                    FROM user_response
                    WHERE user_id = %s
                    GROUP BY DATE(submission_time), exam_id
                '''
                cursor.execute(exam_history_query, (user_id,))
                exam_history = cursor.fetchall()

                connection.close()

                if user_result:
                    user_profile_picture = user_result['profile_picture']
                    user_name = user_result['user_name']

                    return render_template('report.html', user_profile_picture=user_profile_picture, user_name=user_name, exam_history=exam_history)
                else:
                    return "User not found."
        except mysql.connector.Error as err:
            print("Database Error:", err)  # Debug: Print database error
            return "Error connecting to the database.", 500
    else:
        return "Unauthorized access."

@app.route('/view_result/<int:user_id>/<exam_date>/<int:exam_id>')
def view_detailed_report(user_id, exam_date, exam_id):
    try:
        connection = mysql.connector.connect(**db_config)
        if connection.is_connected():
            cursor = connection.cursor(dictionary=True)

            # Fetch user details
            user_query = 'SELECT user_name FROM users WHERE user_id = %s'
            cursor.execute(user_query, (user_id,))
            user_result = cursor.fetchone()

            # Fetch user responses for the specific exam
            user_responses_query = '''
                SELECT qr.ques_id, q.questions, q.option_a, q.option_b, q.option_c, q.option_d, qr.answer AS user_answer, q.correct_ans, qr.submission_time
                FROM user_response AS qr
                JOIN mcq AS q ON qr.ques_id = q.ques_id
                WHERE qr.user_id = %s AND DATE(qr.submission_time) = %s AND qr.exam_id = %s
            '''
            cursor.execute(user_responses_query, (user_id, exam_date, exam_id))
            user_responses = cursor.fetchall()

            # Calculate scores for each response and total score
            for response in user_responses:
                response['score'] = 4 if response['user_answer'] == response['correct_ans'] else 0
            total_score = sum(response['score'] for response in user_responses)

            connection.close()

            if user_result and user_responses:
                user_name = user_result['user_name']

                # Calculate summary information
                total_questions = len(user_responses)
                correct_count = sum(1 for response in user_responses if response['user_answer'] == response['correct_ans'])
                incorrect_count = total_questions - correct_count
                attempted_count = len([response for response in user_responses if response['user_answer']])
                unanswered_count = total_questions - attempted_count

                # Determine overall performance message based on correct_count
                performance_message = ""
                if correct_count == total_questions:
                    performance_message = "Excellent! You answered all questions correctly."
                elif correct_count / total_questions >= 0.7:
                    performance_message = "Well done! You performed well."
                else:
                    performance_message = "Need improvement. Keep practicing."

                return render_template(
                    'detailed_report.html',
                    user_name=user_name,
                    exam_id=exam_id,
                    exam_date=exam_date,
                    user_responses=user_responses,
                    total_questions=total_questions,
                    correct_count=correct_count,
                    incorrect_count=incorrect_count,
                    attempted_count=attempted_count,
                    unanswered_count=unanswered_count,
                    total_score=total_score,
                    performance_message=performance_message
                )
            else:
                return "User or exam details not found."
    except mysql.connector.Error as err:
        print("Database Error:", err)
        return "Error connecting to the database.", 500



if __name__ == '__main__':
    app.run(debug=True)

