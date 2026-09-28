COMICRAFT
AI-Powered Comic Creator
========================

PROJECT DESCRIPTION
-------------------
ComicCraft is a web application that converts a user's story idea
into a 5-panel AI-generated comic.

FEATURES
--------
1. User enters a story prompt.
2. Hugging Face AI generates 5 different comic panels.
3. Each panel uses a different scene and composition.
4. Generated images are displayed in the browser.
5. User can download the complete comic as a PDF.
6. Loading message is displayed during image generation.

TECHNOLOGIES
------------
Python
FastAPI
Uvicorn
Hugging Face Inference API
FLUX.1-schnell
Pillow
FPDF2
HTML
CSS
JavaScript

HOW TO RUN
----------
1. Install Python.
2. Open the project folder in VS Code.
3. Install dependencies:

   python -m pip install -r requirements.txt

4. Set the Hugging Face token:

   $env:HF_TOKEN="YOUR_HUGGINGFACE_TOKEN"

5. Start the application:

   python -m uvicorn main:app --reload

6. Open in browser:

   http://127.0.0.1:8000

IMPORTANT
---------
Do not put the Hugging Face API token inside main.py.
Do not submit the API token with the project.

PROJECT FILES
-------------
main.py             - Main ComicCraft application
main_backup.py      - Backup copy of the application
requirements.txt    - Required Python packages
run.bat              - Starts the application
static/images/      - Generated comic images
README.txt          - Project information

PDF EXPORT
----------
After generating a comic, click:

Download Comic PDF

The application creates ComicCraft.pdf automatically.