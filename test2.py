from flask import Flask, jsonify, send_file, render_template, request, redirect, url_for, session, make_response
from flask_session import Session
from jinja2 import Template
import yaml
import requests
from pprint import pprint
import io
import html

app = Flask(__name__)

# Configure Flask-Session
app.config['SESSION_TYPE'] = 'filesystem'
app.config['SESSION_PERMANENT'] = False
Session(app)

def unescape_emoji(value):
    return html.unescape(value)

# Register the filter in your Flask app
app.jinja_env.filters['unescape_emoji'] = unescape_emoji

@app.route('/')
def index():
    return render_template('form.html')

@app.route('/process_form', methods=['POST'])
def process_form():
    selected_course = request.form['course']
    return redirect(url_for('result', course=selected_course))

@app.route('/result/<course>')
def result(course):
    # Construct the raw file URL of the YAML file in the GitHub repository
    github_repo = 'https://raw.githubusercontent.com/csfeeser/Python/master/demos/'
    yaml_url = github_repo + course + '.txt'
    
    # Make an HTTP GET request to retrieve the YAML file
    response = requests.get(yaml_url)
    
    if response.status_code == 200:
        # Parse the YAML data into Python data
        yaml_data = yaml.safe_load(response.text)
            
        session['yaml_data'] = yaml_data

        return render_template('choices.html', questions=yaml_data)

    else:
        return f'Failed to retrieve the YAML data for {course}.'

@app.route('/download', methods=['POST'])
def download():
    questions = request.form.getlist('selected_questions')
    yaml_data = session.get('yaml_data')
    
    print(type(yaml_data))
    print(type(questions))
    pprint(questions)

    rendered_template = render_template('poll_template.j2', questions=questions, yaml_data=yaml_data)
    
    # Create an in-memory file-like object
    file_stream = io.BytesIO(rendered_template.encode('utf-8'))
    
    # Create a response with the file content
    response = make_response(file_stream.getvalue())
    
    # Set the appropriate headers for file download
    response.headers.set('Content-Type', 'application/octet-stream')
    response.headers.set('Content-Disposition', 'attachment', filename='poll_template.atp')
    
    
    return response


@app.route('/test')
def get_github_data():
    # URL of the YAML file in the GitHub repository
    url = "https://raw.githubusercontent.com/csfeeser/Python/master/demos/questions.yaml"

    try:
        response = requests.get(url)
        data = yaml.safe_load(response.text)
    except Exception as e:
        return jsonify({'error': str(e)})

    display = ""

    for each in data:
        # Define the template
        template_string = '''
        <QUESTION TYPE="mcone" TITLE="{{ question }}">
        {% for answer in answers %}
        <ANSWER ISCORRECT="false">{{ answer }}</ANSWER>
        {% endfor %}
        </QUESTION>
        '''

        # Create a Jinja2 template object
        template = Template(template_string)

        # Render the template with the data
        output = template.render(**each)
        display += output

    with open('data.txt', 'w') as file:
        file.write(display)

    # Send the file to the user for download
    return send_file('data.txt', as_attachment=True)

if __name__ == '__main__':
    app.run(host="0.0.0.0", port=2224, debug=True)

