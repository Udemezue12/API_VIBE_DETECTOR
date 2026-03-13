AI Vibe Code Detector

A backend service that analyzes GitHub repositories and websites to determine whether a codebase was likely generated or heavily assisted by AI tools.

The system scans source code and extracts structural signals that are commonly present in AI-generated projects. These signals are aggregated to produce a vibe score and a classification indicating whether the repository is likely AI-generated.

The API is designed for developers, researchers, and organizations interested in auditing repositories, studying AI-generated code patterns, or evaluating the influence of AI coding assistants on modern software projects.

Features
Repository scanning
Website Scanning

Analyze public GitHub repositories by providing a repository URL. The service downloads the repository, analyzes the codebase, and returns a detection report.

AI pattern detection

The detection engine looks for structural patterns commonly associated with AI-generated code.

Code structure analysis

The scanner evaluates code structure across files and frameworks to identify repeated templates and generated code patterns.

Multiple detection signals

The system aggregates several signals to improve detection accuracy:

Abstract Syntax Tree (AST) structure analysis

JavaScript bundle inspection

Code repetition metrics

Entropy analysis

LLM fingerprint detection

Framework pattern identification

Asynchronous processing

Repository scans run asynchronously using Celery workers, allowing large repositories to be processed without blocking API requests.

Result reporting

The API returns a structured result including:

repository URL

vibe score

AI generation likelihood

detected framework

detected signals and patterns

Project Structure
API_VIBE_DETECTOR
│
├── detector/
│   ├── asgi.py
│   ├── celery_app.py
│   ├── settings.py
│   ├── urls.py
│   └── ...
│
├── vibe_detector/
│   ├── models.py
│   ├── views.py
│   ├── services/
│   ├── repositories/
│   ├── serializers/
│   └── ...
│
├── templates/
├── static/
│
├── manage.py
├── Dockerfile
├── requirements.txt
└── README.md
detector

Contains the Django project configuration, including settings, Celery configuration, and ASGI entrypoints.

vibe_detector

Contains the application logic, including models, API views, services, and repository scanning logic.

templates

HTML templates used for documentation pages or API landing pages.

static

Static assets such as CSS, JavaScript, and images.

Dockerfile

Container configuration used for building and deploying the service.

requirements.txt

Python dependencies required to run the project.

Technology Stack

Python

Django

Django Bolt (API framework)

Celery

Redis

Docker

Detection Methodology

The system uses a combination of structural analysis techniques to estimate whether code was produced by an AI model.

AST Parsing

Source files are parsed into Abstract Syntax Trees to analyze structural patterns that appear frequently in AI-generated code.

Code Repetition Metrics

Generated projects often contain repeated structures or templates. The scanner measures repetition across files and modules.

Entropy Analysis

Entropy measurements help identify overly uniform code structures that can indicate automated generation.

JavaScript Bundle Analysis

For web applications, JavaScript bundles are inspected for common generated patterns.

LLM Fingerprint Detection

The scanner searches for known structural signatures frequently produced by large language models.

The signals are aggregated into a vibe score, which represents the probability that the repository was AI-generated.

API Overview

The service exposes endpoints for submitting repositories for analysis and retrieving scan results.

Submit a repository for scanning
POST /scan

Request body

{
  "repo_url": "https://github.com/user/repository"
}

Response

{
  "task_id": "uuid"
}

The scan runs asynchronously. Use the returned task ID to retrieve results.

Retrieve scan results
GET /scan/{task_id}

Example response

{
  "repo": "https://github.com/user/repository",
  "score": 87,
  "likely_vibecoded": true,
  "signals": {
      "code_patterns": [...],
      "commit_patterns": [...],
      "ast_probability": 0.91
  }
}
Running the Project Locally
Requirements

Python 3.11 or newer

Redis

Docker (optional)

Clone the repository
git clone https://github.com/yourusername/API_VIBE_DETECTOR.git
cd API_VIBE_DETECTOR
Create a virtual environment
python -m venv venv

Activate it:

Linux / macOS

source venv/bin/activate

Windows

venv\Scripts\activate
Install dependencies
pip install -r requirements.txt
Configure environment variables

Create a .env file in the project root.

Example:

DEBUG=True
SECRET_KEY=your-secret-key
REDIS_URL=redis://127.0.0.1:6379/0
ALLOWED_HOSTS=localhost,127.0.0.1
Run database migrations
python manage.py migrate
Start Redis

If Redis is installed locally:

redis-server
Start the Celery worker
celery -A detector worker -l info
Start the API server
python manage.py runbolt --dev

The API will be available at:

http://localhost:8000

API documentation:

http://localhost:8000/docs
Running with Docker

Build the container:

docker build -t vibe-detector .

Run the container:

docker run -p 8000:8000 vibe-detector
Environment Variables
Variable	Description
DEBUG	Enable or disable debug mode
SECRET_KEY	Django secret key
REDIS_URL	Redis connection string
ALLOWED_HOSTS	Allowed hostnames
Background Task Processing

Repository scans are processed asynchronously using Celery.

This prevents long-running scans from blocking API requests and allows the service to scale horizontally by adding additional workers.

Limitations

Only public repositories can be analyzed.

Detection is probabilistic and should not be treated as a definitive classification.

Large repositories may take longer to process.

Future Improvements

Possible future enhancements include:

support for additional programming languages

improved detection signals

commit history analysis

repository comparison tools

model-assisted pattern classification

License

This project is released under the MIT License.