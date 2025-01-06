# Frontend Documentation

## Overview

The frontend is a React application that provides a user interface for:

- Registering new speakers
- Identifying speakers from audio samples
- Displaying audio waveforms
- Showing registered speakers

## Key Components

### State Management
`const [speakers, setSpeakers] = useState([]); // Stores list of registered speakers`
`const [selectedFile, setSelectedFile] = useState(null); // Currently selected audio file`
`const [result, setResult] = useState(null); // Speaker identification results`
`const [newSpeakerId, setNewSpeakerId] = useState(''); // ID for new speaker registration`
`const [newSpeakerName, setNewSpeakerName] = useState(''); // Name for new speaker`
`const [waveform, setWaveform] = useState(null); // Audio waveform visualization`

### Main Functions

1. `fetchSpeakers()`:

   - Retrieves list of registered speakers from backend
   - Called on component mount

2. `handleFileSelect(event)`:

   - Handles audio file selection
   - Triggers waveform generation

3. `generateWaveform(file)`:

   - Creates visual representation of audio file
   - Displays waveform below file input

4. `handleIdentify()`:

   - Sends audio for speaker identification
   - Displays results with confidence score

5. `handleRegister()`:
   - Registers new speaker with audio sample
   - Updates speaker list after registration

## API Endpoints Used

- GET `/speakers`: Get list of registered speakers
- POST `/identify`: Identify speaker from audio
- POST `/register`: Register new speaker
- POST `/audio/waveform`: Generate audio waveform


# Backend API Documentation

## Overview

FastAPI backend providing speaker recognition functionality and API endpoints.

## Endpoints

### GET /speakers

- Returns list of all registered speakers
- Response: `{"speakers": {speaker_id: speaker_name, ...}}`

### POST /identify

- Identifies speaker from audio file
- Input: Audio file (multipart/form-data)
- Response:
  ```json
  {
    "speaker_id": "string",
    "name": "string",
    "confidence": float
  }
  ```

### POST /register

- Registers new speaker with audio sample
- Input:
  - Audio file (multipart/form-data)
  - speaker_id (query parameter)
  - speaker_name (optional query parameter)
- Response: `{"message": "Speaker {id} registered successfully"}`

### POST /audio/waveform

- Generates waveform visualization
- Input: Audio file (multipart/form-data)
- Response: `{"waveform": "base64_encoded_image"}`

## Error Handling

- File not found: 404
- Processing errors: 500
- Invalid input: 400


# Speaker Handler Documentation

## Overview

Core class handling speaker recognition functionality:

- Feature extraction
- Speaker identification
- Speaker registration
- Data persistence

## Key Methods

### **init**(dataset_path)

- Initializes handler with dataset path
- Creates storage for speaker features and names
- Loads existing speakers

### extract_features(audio_path)

- Extracts MFCC features from audio
- Returns normalized feature vector

### identify_speaker(audio_path)

- Compares audio with registered speakers
- Returns best match and confidence score

### add_speaker_sample(speaker_id, audio_path, original_filename)

- Registers new speaker or adds sample
- Saves audio file and extracts features
- Updates speaker database

### save_speakers() / load_saved_speakers()

- Handles persistence of speaker data
- Saves/loads from JSON file

## Data Structure
json
{
"speaker_id": {
"features": [...],
"name": "string",
"files": [...]
}
}


Audio Processor Documentation
Overview
Handles audio visualization and processing:
Waveform generation
Audio file handling
Matplotlib visualization
Key Methods
generate_waveform(audio_path)
Loads audio file using librosa
Creates waveform visualization
Returns base64 encoded image
Dependencies
librosa: Audio processing
matplotlib: Visualization
numpy: Numerical operations

`Python Dependencies`
fastapi
uvicorn
librosa
numpy
matplotlib
python-multipart
slowapi

`Node.js Dependencies`
react
@mui/material
axios

`Environment Setup`
Backend:
`pip install -r requirements.txt
uvicorn app.api.routes:app --reload`

Frontend:
`npm install
npm start`

File Structure
`project/
├── backend/
│ ├── app/
│ │ ├── api/
│ │ │ └── routes.py
│ │ ├── data/
│ │ │ └── speaker_handler.py
│ │ └── utils/
│ │ └── audio_processor.py
│ └── requirements.txt
└── frontend/
├── src/
│ └── App.js
└── package.json`
