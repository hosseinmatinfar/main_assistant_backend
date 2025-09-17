import os
import openai
import logging
from fastapi import FastAPI, UploadFile, File
from fastapi.responses import StreamingResponse, JSONResponse
from dotenv import load_dotenv

# Load API key from .env file during local testing
load_dotenv()

# --- Configure Logging ---
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)

# --- OpenAI Initial Setup ---
api_key = os.getenv("OPENAI_API_KEY")
if not api_key:
    raise ValueError("OpenAI API key not found. Please set it in Vercel.")

client = openai.OpenAI(api_key=api_key)

# --- Create FastAPI Application ---
app = FastAPI(title="Mia AI Agent")

@app.get("/")
def read_root():
    return {"message": "Mia is online and ready to assist you."}

@app.post("/process-audio/")
async def process_audio(file: UploadFile = File(...)):
    logging.info(f"Audio file '{file.filename}' received for processing.")

    try:
        # --- Step 1: Convert audio to text with Whisper ---
        audio_data = await file.read()
        transcription = client.audio.transcriptions.create(
            model="whisper-1",
            file=(file.filename, audio_data)
        )
        user_text = transcription.text
        logging.info(f"Extracted text: {user_text}")

        # --- Step 2: Get a response from GPT (Mia’s personality) ---
        chat_completion = client.chat.completions.create(
            model="gpt-4o",
            messages=[
                {"role": "system", "content": "You are Mia, a precise, reliable, and friendly laboratory assistant for a pharmacist."},
                {"role": "user", "content": user_text}
            ]
        )
        ai_response_text = chat_completion.choices[0].message.content
        logging.info(f"Mia response (text): {ai_response_text}")

        # --- Step 3: Convert response to speech with TTS ---
        ai_response_speech = client.audio.speech.create(
            model="tts-1",
            voice="alloy",
            input=ai_response_text
        )

        # --- Step 4: Stream audio back to Flutter app ---
        return StreamingResponse(ai_response_speech.iter_bytes(), media_type="audio/mpeg")

    except Exception as e:
        logging.error(f"Mia encountered an error: {e}", exc_info=True)
        # Professional error response
        return JSONResponse(
            status_code=500,
            content={
                "agent": "Mia",
                "error": "Sorry, Mia ran into a problem while processing your request.",
                "details": str(e)  # 🔒 Remove in production for security
            }
        )
