from flask import Flask, jsonify, send_file, render_template, request, redirect, url_for, session, make_response
from flask_session import Session
from jinja2 import Template
import yaml
import requests
from pprint import pprint
import io
import html
from datetime import datetime

app = Flask(__name__)
app.secret_key = "any random string"

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/process_form', methods=['POST'])
def process_form():
    # Retrieve the selected course from the form
    selected_course = request.form['course']
    return redirect(url_for('result', course=selected_course))

@app.route('/result/<course>', methods=["GET", "POST"])
def result(course):
    if request.method == "POST":
        # Retrieve form data
        question = request.form.get('question')
        answer_a = request.form.get('answer_a')
        answer_b = request.form.get('answer_b')
        answer_c = request.form.get('answer_c')
        answer_d = request.form.get('answer_d')

        # Check if question and at least one answer are provided
        if not question or not any([answer_a, answer_b, answer_c, answer_d]):
            return "Error: Please provide a question and at least one answer."

        # Create answers list, excluding any empty values
        answers = [answer for answer in [answer_a, answer_b, answer_c, answer_d] if answer]

        # Construct new_question dictionary
        new_question = {"question": question, "answers": answers, "day": "CUSTOM"}

        if session.get("add"):
            session["add"].append(new_question)
        else:
            session["add"]= [new_question]

        return redirect(f"/result/{course}")

    else:
        # Construct the raw file URL of the YAML file in the GitHub repository
        github_repo = 'https://raw.githubusercontent.com/csfeeser/Python/master/demos/'
        yaml_url = github_repo + course + '.txt'
        
        # Make an HTTP GET request to retrieve the YAML file
        response = requests.get(yaml_url)
        
        if response.status_code == 200:
            # Parse the YAML data into Python data
            yaml_data = yaml.safe_load(response.text)
                
            if session.get("add"):
                yaml_data.extend(session["add"])

            session['yaml_data'] = yaml_data
            session['course name']= course

            return render_template('choices.html', questions=yaml_data)

        else:
            return f'Failed to retrieve the YAML data for {course}.'

@app.route('/download', methods=['POST'])
def download():
    try:
        # Retrieve the selected questions from the form
        questions = request.form.getlist('selected_questions')
        yaml_data = session.get('yaml_data')
        
        print(type(yaml_data))
        print(type(questions))
        pprint(questions)

        # Render the poll template with the selected questions and YAML data
        rendered_template = render_template('poll_template.j2', questions=questions, yaml_data=yaml_data)
        
        # Create an in-memory file-like object
        file_stream = io.BytesIO(rendered_template.encode('utf-8'))
        
        # Create a response with the file content
        response = make_response(file_stream.getvalue())
        
        # Create timestamp and filename
        today = datetime.today()
        formatted_date = today.strftime("%m-%d-%Y")
        course_name= session['course name']
        file_name= f"{course_name}-poll-{formatted_date}.atp"
        
        # Set the appropriate headers for file download
        response.headers.set('Content-Type', 'application/octet-stream')
        response.headers.set('Content-Disposition', 'attachment', filename=file_name)
        
        return response

    except Exception as e:
        return f"There was an error: {{e}}"

@app.route('/addnew')
def add_new():
    if session['course name']:
        return render_template('addnew.j2', course_name=session['course name'])
    else:
        return '<a href="/" class="back-link">You have not selected a course. Return to the main page.</a>'

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=2224, debug=True)
