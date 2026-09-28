import time
import html
from pathlib import Path

from fastapi import FastAPI, Form
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from huggingface_hub import InferenceClient
from fpdf import FPDF

app = FastAPI(title="ComicCraft")
import os
LATEST_IMAGES = []


def create_pdf():
    pdf = FPDF()
    pdf.set_auto_page_break(auto=True, margin=15)

    for number, image_path in enumerate(LATEST_IMAGES, start=1):
        pdf.add_page()

        pdf.set_font("Arial", "B", 20)
        pdf.cell(0, 15, f"ComicCraft - Panel {number}", ln=True, align="C")
        pdf.ln(5)

        pdf.image(str(image_path), x=15, y=35, w=180)

    pdf.output("ComicCraft.pdf")
    return "ComicCraft.pdf"


# -----------------------------
# 
# -----------------------------

IMAGE_DIR = Path("static/images")
IMAGE_DIR.mkdir(parents=True, exist_ok=True)

app.mount(
    "/static",
    StaticFiles(directory="static"),
    name="static"
)


# -----------------------------
# Hugging Face
# -----------------------------

HF_TOKEN = os.getenv("HF_TOKEN")

if not HF_TOKEN:
    raise RuntimeError(
        "HF_TOKEN is missing. Set your Hugging Face token in the terminal."
    )

client = InferenceClient(
    api_key=HF_TOKEN,
    provider="auto"
)

MODEL = "black-forest-labs/FLUX.1-schnell"


# -----------------------------
# Home Page
# -----------------------------

@app.get("/", response_class=HTMLResponse)
def home():

    return """
    <!DOCTYPE html>

    <html>

    <head>

        <title>ComicCraft</title>

        <style>

            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: #f4f4f4;
            }

            header {
                background: #222;
                color: white;
                text-align: center;
                padding: 30px;
            }

            header h1 {
                margin: 0;
                font-size: 42px;
            }

            header p {
                font-size: 18px;
            }

            .container {
                max-width: 750px;
                margin: 60px auto;
                background: white;
                padding: 40px;
                border-radius: 15px;
                box-shadow: 0 5px 20px rgba(0,0,0,0.12);
                text-align: center;
            }

            textarea {
                width: 90%;
                height: 160px;
                padding: 15px;
                font-size: 17px;
                border: 1px solid #ccc;
                border-radius: 10px;
                resize: vertical;
            }

            button {
                margin-top: 25px;
                padding: 15px 35px;
                font-size: 17px;
                border: none;
                border-radius: 8px;
                background: #222;
                color: white;
                cursor: pointer;
            }

            button:hover {
                background: #444;
            }

        </style>

    </head>


    <body>

        <header>

            <h1>ComicCraft</h1>

            <p>
                AI-Powered Comic Creator
            </p>

        </header>


        <div class="container">

            <h2>Create Your Comic</h2>

            <p>
                Enter your story idea and generate a 5-panel comic.
            </p>


            <form action="/generate" method="post">

                <textarea
                    name="story"
                    placeholder="Example: A young superhero saves Chennai from a giant robot..."
                    required
                ></textarea>


                <br>


                <button type="submit">
                    Generate Comic
                </button>

            </form>

        </div>

    </body>

    </html>
    """


# -----------------------------
# Generate Comic
# -----------------------------

@app.post("/generate", response_class=HTMLResponse)
def generate(story: str = Form(...)):

    # Keep the original story for AI prompts
    original_story = story.strip()

    # Escape story before putting it into HTML
    safe_story = html.escape(original_story)


    # Each panel has a DIFFERENT scene.
    scenes = [
        "wide establishing shot introducing the setting and main character",
        "character-focused scene showing the hero beginning the adventure",
        "dramatic conflict scene showing the main problem or enemy",
        "dynamic action scene showing the hero fighting or solving the problem",
        "emotional final scene showing the ending and resolution"
    ]


    panels = []

    LATEST_IMAGES.clear()
    # Generate 5 different images
    for number, scene in enumerate(scenes, start=1):

        print(f"Generating Panel {number}...")


        prompt = f"""
        Create panel {number} of a colorful modern comic book.

        Main story:
        {original_story}

        Scene for this panel:
        {scene}

        Maintain the same characters, clothing, art style
        and world throughout the comic.

        Panel {number} must have a different composition
        and camera angle from the other panels.

        Detailed characters.
        Detailed environment.
        Expressive faces.
        Cinematic lighting.
        Vibrant comic-book illustration.
        High quality.
        No watermark.
        No written text.
        No speech bubbles.
        """


        filename = f"panel_{number}_{int(time.time())}.png"

        filepath = IMAGE_DIR / filename


        try:

            image = client.text_to_image(
                prompt=prompt,
                model=MODEL,
                width=768,
                height=512,
                num_inference_steps=4,
                seed=1000 + number
            )


            image.save(filepath)
            LATEST_IMAGES.append(filepath)


            print(f"Panel {number} created.")


            panels.append(
                {
                    "number": number,
                    "image": f"/static/images/{filename}",
                    "scene": scene,
                    "error": None
                }
            )


        except Exception as e:

            print(f"Panel {number} ERROR: {e}")


            panels.append(
                {
                    "number": number,
                    "image": None,
                    "scene": scene,
                    "error": str(e)
                }
            )


    # -----------------------------
    # Build HTML for panels
    # -----------------------------

    panel_html = ""


    for panel in panels:

        if panel["image"]:

            image_content = f"""
            <img
                src="{panel['image']}"
                alt="Comic Panel {panel['number']}"
            >
            """

        else:

            image_content = f"""
            <div class="error-box">

                <strong>
                    Panel {panel['number']} image failed
                </strong>

                <p>
                    {html.escape(panel['error'] or '')}
                </p>

            </div>
            """


        panel_html += f"""

        <div class="panel">

            <h2>
                Panel {panel['number']}
            </h2>


            <div class="image-container">

                {image_content}

            </div>


            <p class="scene">

                {html.escape(panel['scene'])}

            </p>

        </div>

        """


    return f"""

    <!DOCTYPE html>

    <html>

    <head>

        <title>
            ComicCraft - Preview
        </title>


        <style>

            body {{
                margin: 0;
                font-family: Arial, sans-serif;
                background: #eeeeee;
            }}


            header {{
                background: #222;
                color: white;
                text-align: center;
                padding: 30px;
            }}


            header h1 {{
                margin: 0;
                font-size: 40px;
            }}


            .story-title {{
                text-align: center;
                margin: 30px auto;
                max-width: 900px;
            }}


            .comic {{
                max-width: 900px;
                margin: auto;
            }}


            .panel {{
                background: white;
                margin: 30px 20px;
                padding: 25px;
                border-radius: 15px;
                box-shadow: 0 4px 15px rgba(0,0,0,0.15);
            }}


            .panel h2 {{
                text-align: center;
                font-size: 28px;
            }}


            .image-container {{
                width: 100%;
                min-height: 400px;
                background: #ddd;
                border-radius: 12px;
                overflow: hidden;
                display: flex;
                align-items: center;
                justify-content: center;
            }}


            .image-container img {{
                width: 100%;
                height: 100%;
                min-height: 400px;
                object-fit: cover;
                display: block;
            }}


            .scene {{
                text-align: center;
                font-size: 17px;
                line-height: 1.6;
                margin-top: 20px;
            }}


            .error-box {{
                padding: 50px;
                text-align: center;
                color: #777;
            }}


            .back {{
                display: block;
                width: fit-content;
                margin: 35px auto;
                padding: 14px 30px;
                background: #222;
                color: white;
                text-decoration: none;
                border-radius: 8px;
            }}


        </style>

    </head>


    <body>


        <header>

            <h1>
                ComicCraft
            </h1>

            <p>
                AI Generated Comic Preview
            </p>

        </header>


        <div class="story-title">

            <h2>
                Your Story
            </h2>

            <p>
                {safe_story}
            </p>

        </div>


        <div class="comic">

            {panel_html}


                        <a
                class="back"
                href="/export"
            >
                📄 Download Comic PDF
            </a>

            <a
                class="back"
                href="/"
            >
                ← Create Another Comic
            </a>

        </div>


    </body>

    </html>

    """

@app.get("/export")
def export_pdf():

    if not LATEST_IMAGES:
        return HTMLResponse(
            "<h2>Please generate a comic first.</h2>"
        )

    pdf_file = create_pdf()

    return FileResponse(
        pdf_file,
        media_type="application/pdf",
        filename="ComicCraft.pdf"
    )