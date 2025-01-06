import os
import json
import shutil
import librosa
import numpy as np
from collections import defaultdict
from scipy.stats import norm

class SpeakerHandler:
    def __init__(self, dataset_path):
        self.dataset_path = dataset_path
        self.registered_path = "registered_speakers"
        self.speaker_features = defaultdict(list)
        self.speaker_names = {}
        self.storage_file = "speakers_database.json"
        
        os.makedirs(self.registered_path, exist_ok=True)
        
        self.load_speakers()
        self.load_saved_speakers()

    def save_speakers(self):
        """Save speaker features and metadata to file"""
        data = {
            speaker_id: {
                'features': [features.tolist() for features in feature_list],
                'name': self.speaker_names.get(speaker_id, f"Speaker {speaker_id}"),
                'files': self.get_speaker_files(speaker_id)
            }
            for speaker_id, feature_list in self.speaker_features.items()
        }
        
        with open(self.storage_file, 'w') as f:
            json.dump(data, f, indent=2) 

    def get_speaker_files(self, speaker_id):
        """Get list of audio files for a speaker"""
        speaker_dir = os.path.join(self.registered_path, speaker_id)
        if os.path.exists(speaker_dir):
            return [f for f in os.listdir(speaker_dir) if f.endswith(('.wav', '.flac', '.mp3'))]
        return []

    def add_speaker_sample(self, speaker_id, audio_path, original_filename):
        """Add a new audio sample for a speaker"""
        speaker_dir = os.path.join(self.registered_path, speaker_id)
        os.makedirs(speaker_dir, exist_ok=True)
        
        new_filename = f"{len(self.get_speaker_files(speaker_id)) + 1}_{original_filename}"
        new_path = os.path.join(speaker_dir, new_filename)
        shutil.copy2(audio_path, new_path)
        
        features = self.extract_features(new_path)
        if features is not None:
            self.speaker_features[speaker_id].append(features)
            self.save_speakers()
            return True
        return False

    def get_speaker_info(self, speaker_id):
        """Get detailed information about a speaker"""
        if speaker_id in self.speaker_names:
            return {
                'id': speaker_id,
                'name': self.speaker_names[speaker_id],
                'samples': self.get_speaker_files(speaker_id),
                'total_samples': len(self.speaker_features[speaker_id])
            }
        return None

    def get_all_speakers(self):
        """Get information about all registered speakers"""
        return {
            speaker_id: self.get_speaker_info(speaker_id)
            for speaker_id in self.speaker_names
        }

    def load_saved_speakers(self):
        """Load saved speaker features from file"""
        if os.path.exists(self.storage_file):
            with open(self.storage_file, 'r') as f:
                data = json.load(f)
                
            for speaker_id, speaker_data in data.items():
                features = [np.array(feature_list) for feature_list in speaker_data['features']]
                self.speaker_features[speaker_id].extend(features)
                self.speaker_names[speaker_id] = speaker_data['name']
                print(f"Loaded saved speaker: {speaker_id}")

    def extract_features(self, audio_path):
        try:
            y, sr = librosa.load(audio_path, duration=5)
            
            mfcc = librosa.feature.mfcc(y=y, sr=sr, n_mfcc=40)
            delta_mfcc = librosa.feature.delta(mfcc)
            delta2_mfcc = librosa.feature.delta(mfcc, order=2)
            
            mel_spect = librosa.feature.melspectrogram(y=y, sr=sr, n_mels=128)
            mel_spect_db = librosa.power_to_db(mel_spect, ref=np.max)
            
            spectral_centroids = librosa.feature.spectral_centroid(y=y, sr=sr)
            spectral_rolloff = librosa.feature.spectral_rolloff(y=y, sr=sr)
            
            zcr = librosa.feature.zero_crossing_rate(y)
            
            features = np.concatenate([
                np.mean(mfcc, axis=1),
                np.std(mfcc, axis=1),
                np.mean(delta_mfcc, axis=1),
                np.mean(delta2_mfcc, axis=1),
                np.mean(mel_spect_db, axis=1),
                np.std(mel_spect_db, axis=1),
                np.mean(spectral_centroids, axis=1),
                np.mean(spectral_rolloff, axis=1),
                np.mean(zcr, axis=1)
            ])
            
            features = (features - np.mean(features)) / np.std(features)
            
            return features
            
        except Exception as e:
            print(f"Error processing {audio_path}: {str(e)}")
            return None

    def calculate_similarity(self, features1, features2):
        """Calculate similarity between two feature sets using multiple metrics"""
        euclidean_dist = np.linalg.norm(features1 - features2)
        
        cosine_sim = np.dot(features1, features2) / (np.linalg.norm(features1) * np.linalg.norm(features2))
        
        similarity = 0.7 * (1 / (1 + euclidean_dist)) + 0.3 * ((cosine_sim + 1) / 2)
        
        return similarity

    def identify_speaker(self, audio_path):
        test_features = self.extract_features(audio_path)
        if test_features is None:
            return None, 0.0

        best_match = None
        best_score = -float('inf')
        scores = []

        for speaker_id in self.speaker_features:
            speaker_samples = self.speaker_features[speaker_id]
            sample_scores = []
            
            for sample_features in speaker_samples:
                similarity = self.calculate_similarity(test_features, sample_features)
                sample_scores.append(similarity)
            
            top_scores = sorted(sample_scores, reverse=True)[:3]
            avg_score = np.mean(top_scores)
            scores.append(avg_score)
            
            if avg_score > best_score:
                best_score = avg_score
                best_match = speaker_id

        if scores:
            mean_score = np.mean(scores)
            std_score = np.std(scores) if len(scores) > 1 else 0.1
            confidence = norm.cdf((best_score - mean_score) / (std_score + 1e-6))
            confidence = (confidence - 0.5) * 2
            confidence = max(0, min(1, confidence))
        else:
            confidence = 0.0

        return best_match, confidence

    def get_speaker_features(self, speaker_id):
        """Get average features for a speaker"""
        if speaker_id in self.speaker_features and len(self.speaker_features[speaker_id]) > 0:
            return np.mean(self.speaker_features[speaker_id], axis=0)
        return None

    def load_speakers(self):
        """Load speakers from LibriSpeech dataset"""
        print("Loading speakers from LibriSpeech...")
        
        for speaker_id in os.listdir(self.dataset_path):
            speaker_path = os.path.join(self.dataset_path, speaker_id)
            if os.path.isdir(speaker_path):
                for chapter_dir in os.listdir(speaker_path):
                    chapter_path = os.path.join(speaker_path, chapter_dir)
                    if os.path.isdir(chapter_path):
                        audio_files = [f for f in os.listdir(chapter_path) if f.endswith('.flac')][:3]
                        for audio_file in audio_files:
                            audio_path = os.path.join(chapter_path, audio_file)
                            self.add_speaker_sample(speaker_id, audio_path, audio_file)
                print(f"Loaded speaker: {speaker_id}") 

    def delete_speaker(self, speaker_id):
        """Delete a speaker and all their data"""
        try:
            if speaker_id in self.speaker_features:
                del self.speaker_features[speaker_id]
            if speaker_id in self.speaker_names:
                del self.speaker_names[speaker_id]
            
            speaker_dir = os.path.join(self.registered_path, speaker_id)
            if os.path.exists(speaker_dir):
                shutil.rmtree(speaker_dir)
            
            self.save_speakers()
            return True
        except Exception as e:
            print(f"Error deleting speaker {speaker_id}: {str(e)}")
            return False

    def update_speaker_info(self, speaker_id, new_name=None):
        """Update speaker information"""
        if speaker_id in self.speaker_names:
            if new_name:
                self.speaker_names[speaker_id] = new_name
            self.save_speakers()
            return True
        return False

    def compare_speakers(self, audio_path1, audio_path2):
        """Compare two audio files to check if they're the same speaker"""
        features1 = self.extract_features(audio_path1)
        features2 = self.extract_features(audio_path2)
        
        if features1 is None or features2 is None:
            return None, 0.0
        
        similarity = self.calculate_similarity(features1, features2)
        is_same_speaker = similarity > 0.7
        
        return is_same_speaker, similarity 