import numpy as np
import librosa
import matplotlib.pyplot as plt
import io
import base64

class AudioProcessor:
    @staticmethod
    def generate_waveform(audio_path, preprocessed=False):
        """Generate waveform visualization"""
        y, sr = librosa.load(audio_path)

        plt.figure(figsize=(10, 3))
        plt.plot(y)
        plt.title('Audio Waveform')
        plt.xlabel('Time')
        plt.ylabel('Amplitude')
        plt.grid(True)

        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        plt.close()
        buf.seek(0)
        
        image_base64 = base64.b64encode(buf.getvalue()).decode('utf-8')
        return image_base64 