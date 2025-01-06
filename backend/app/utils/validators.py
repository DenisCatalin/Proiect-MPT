from pydantic import BaseModel, validator
from typing import Optional

class SpeakerUpdate(BaseModel):
    new_name: str

    @validator('new_name')
    def name_must_be_valid(cls, v):
        if not v or len(v) < 2:
            raise ValueError('Name must be at least 2 characters long')
        return v

class AudioFile(BaseModel):
    file: UploadFile

    @validator('file')
    def validate_audio_file(cls, v):
        if not v.content_type.startswith('audio/'):
            raise ValueError('File must be an audio file')
        return v 