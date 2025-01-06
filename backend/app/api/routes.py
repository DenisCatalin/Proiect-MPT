from fastapi import FastAPI, File, UploadFile, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from app.utils.audio_processor import AudioProcessor
from app.data.speaker_handler import SpeakerHandler
import os

app = FastAPI()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize Speaker handler
speaker_handler = SpeakerHandler(dataset_path="C:/Users/Denis/Desktop/LibriSpeech/dev-clean")

@app.get("/speakers")
async def get_speakers():
    """Get list of all speakers"""
    return {"speakers": speaker_handler.speaker_names}

@app.post("/identify")
async def identify_speaker(audio: UploadFile = File(...)):
    """Identify speaker from audio file"""
    temp_path = f"temp_{audio.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            content = await audio.read()
            buffer.write(content)
        
        speaker_id, confidence = speaker_handler.identify_speaker(temp_path)
        if speaker_id:
            return {
                "speaker_id": speaker_id,
                "name": speaker_handler.speaker_names.get(speaker_id, "Unknown"),
                "confidence": confidence
            }
        return {"error": "No speaker identified"}
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/register")
async def register_speaker(speaker_id: str, speaker_name: str = None, audio: UploadFile = File(...)):
    """Register a new speaker"""
    temp_path = f"temp_{audio.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            content = await audio.read()
            buffer.write(content)
        
        if speaker_handler.add_speaker_sample(speaker_id, temp_path, audio.filename):
            if speaker_name:
                speaker_handler.speaker_names[speaker_id] = speaker_name
                speaker_handler.save_speakers()
            return {"message": f"Speaker {speaker_id} registered successfully"}
        return {"error": "Failed to process audio"}
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)

@app.post("/audio/waveform")
async def generate_waveform(audio: UploadFile = File(...)):
    """Generate waveform visualization for audio file"""
    temp_path = f"temp_{audio.filename}"
    try:
        with open(temp_path, "wb") as buffer:
            content = await audio.read()
            buffer.write(content)
        
        waveform = AudioProcessor.generate_waveform(temp_path)
        return {"waveform": waveform}
    
    finally:
        if os.path.exists(temp_path):
            os.remove(temp_path)
