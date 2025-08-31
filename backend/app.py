from flask import Flask, request, jsonify, send_file, make_response
from flask_cors import CORS
import os
from werkzeug.utils import secure_filename
import docx2txt
import PyPDF2
import google.generativeai as genai

app = Flask(__name__)
CORS(app)

# Add a root route for a welcome message
@app.route('/')
def home():
    return 'Welcome to the AI Interview Preparation Backend! Use /analyze to POST your resume or skills.'

UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'pdf', 'docx'}
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# Set your Gemini API key here or use an environment variable
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY', 'YOUR_GEMINI_API_KEY')
genai.configure(api_key=GEMINI_API_KEY)

try:
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content("Say hello in one sentence.")
    print("API Key is working! Response:")
    print(response.text)
except Exception as e:
    print("API Key test failed:", e)

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def extract_text_from_pdf(filepath):
    text = ''
    with open(filepath, 'rb') as f:
        reader = PyPDF2.PdfReader(f)
        for page in reader.pages:
            text += page.extract_text() or ''
    return text

def extract_text_from_docx(filepath):
    return docx2txt.process(filepath)

def generate_interview_content(text):
    prompt = (
        "You are an experienced technical recruiter. Given the following resume or skillset, "
        "provide a detailed, structured output in markdown format with clear sections and tables. "
        "The output should include:\n"
        "1. **Summary of Candidate**\n"
        "2. **Likely Interview Questions** (as a markdown bullet list with topics and numbered sublist with the questions)\n"
        "3. **Recommended Topics to Study** (as a markdown bullet list)\n"
        "4. **Tips for Interview** (as a markdown bullet list)\n\n"
        "Resume/Skills:\n"
        f"{text}\n\n"
        "Format your response using markdown for tables and lists. Do not use code blocks."
    )
    model = genai.GenerativeModel("gemini-2.0-flash")
    response = model.generate_content(prompt)
    return response.text

@app.route('/analyze', methods=['POST'])
def analyze():
    if 'file' in request.files:
        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            file.save(filepath)
            ext = filename.rsplit('.', 1)[1].lower()
            if ext == 'pdf':
                text = extract_text_from_pdf(filepath)
            elif ext == 'docx':
                text = extract_text_from_docx(filepath)
            else:
                return jsonify({'error': 'Unsupported file type'}), 400
            if not text.strip():
                return jsonify({'error': 'Could not extract text from file'}), 400
            ai_output = generate_interview_content(text)
            return jsonify({'result': ai_output})
        else:
            return jsonify({'error': 'Invalid file type'}), 400
    elif request.is_json and 'skills' in request.json:
        skills = request.json['skills']
        if not skills.strip():
            return jsonify({'error': 'No skills provided'}), 400
        ai_output = generate_interview_content(skills)
        return jsonify({'result': ai_output})
    else:
        return jsonify({'error': 'No input provided'}), 400

if __name__ == '__main__':
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)
