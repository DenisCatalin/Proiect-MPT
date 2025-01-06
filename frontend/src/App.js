import React, { useState, useEffect } from 'react';
import { Container, Paper, Button, Typography, Box } from '@mui/material';
import axios from 'axios';

function App() {
  const [speakers, setSpeakers] = useState([]);
  const [selectedFile, setSelectedFile] = useState(null);
  const [result, setResult] = useState(null);
  const [newSpeakerId, setNewSpeakerId] = useState('');
  const [newSpeakerName, setNewSpeakerName] = useState('');
  const [waveform, setWaveform] = useState(null);

  useEffect(() => {
    fetchSpeakers();
  }, []);

  const fetchSpeakers = async () => {
    try {
      const response = await axios.get('http://localhost:8000/speakers');
      setSpeakers(response.data.speakers);
    } catch (error) {
      console.error('Error fetching speakers:', error);
    }
  };

  const handleFileSelect = (event) => {
    const file = event.target.files[0];
    setSelectedFile(file);
    setResult(null);
    if (file) {
      generateWaveform(file);
    }
  };

  const generateWaveform = async (file) => {
    const formData = new FormData();
    formData.append('audio', file);

    try {
      const response = await axios.post('http://localhost:8000/audio/waveform', formData);
      setWaveform(response.data.waveform);
    } catch (error) {
      console.error('Error generating waveform:', error);
    }
  };

  const handleIdentify = async () => {
    if (!selectedFile) {
      alert('Please select an audio file first');
      return;
    }

    const formData = new FormData();
    formData.append('audio', selectedFile);

    try {
      const response = await axios.post('http://localhost:8000/identify', formData);
      setResult(response.data);
    } catch (error) {
      console.error('Error identifying speaker:', error);
      setResult({ error: 'Failed to identify speaker' });
    }
  };

  const handleRegister = async () => {
    if (!selectedFile || !newSpeakerId) {
      alert('Please select an audio file and enter a speaker ID');
      return;
    }

    const formData = new FormData();
    formData.append('audio', selectedFile);

    try {
      const response = await axios.post(
        `http://localhost:8000/register?speaker_id=${newSpeakerId}&speaker_name=${newSpeakerName || ''}`, 
        formData
      );
      alert(response.data.message);
      fetchSpeakers();
      setNewSpeakerId('');
      setNewSpeakerName('');
      setSelectedFile(null);
    } catch (error) {
      console.error('Error registering speaker:', error);
      alert('Failed to register speaker');
    }
  };

  return (
    <Container maxWidth="md">
      <Box sx={{ my: 4 }}>
        <Typography variant="h4" component="h1" gutterBottom align="center">
          Speaker Recognition System
        </Typography>

        <Paper sx={{ p: 3, mb: 2 }}>
          <input
            type="file"
            accept="audio/*"
            onChange={handleFileSelect}
            style={{ marginBottom: '1rem', display: 'block' }}
          />

          <Box sx={{ mb: 2 }}>
            <input
              type="text"
              placeholder="Enter new speaker ID"
              value={newSpeakerId}
              onChange={(e) => setNewSpeakerId(e.target.value)}
              style={{ marginBottom: '1rem', display: 'block' }}
            />
            <input
              type="text"
              placeholder="Enter speaker name (optional)"
              value={newSpeakerName}
              onChange={(e) => setNewSpeakerName(e.target.value)}
              style={{ marginBottom: '1rem', display: 'block' }}
            />
            <Button 
              variant="contained" 
              onClick={handleRegister}
              disabled={!selectedFile || !newSpeakerId}
              style={{ marginRight: '1rem' }}
            >
              Register New Speaker
            </Button>
            <Button 
              variant="contained" 
              onClick={handleIdentify}
              disabled={!selectedFile}
            >
              Identify Speaker
            </Button>
          </Box>

          {waveform && (
            <Box sx={{ mt: 2, mb: 2 }}>
              <Typography variant="h6">Waveform:</Typography>
              <img 
                src={`data:image/png;base64,${waveform}`} 
                alt="Audio Waveform" 
                style={{ width: '100%' }} 
              />
            </Box>
          )}

          {result && (
            <Box sx={{ mt: 2 }}>
              <Typography variant="h6">Results:</Typography>
              {result.error ? (
                <Typography color="error">{result.error}</Typography>
              ) : (
                <Typography>
                  Speaker ID: {result.speaker_id}
                  <br />
                  Name: {result.name}
                  <br />
                  Confidence: {(result.confidence * 100).toFixed(2)}%
                </Typography>
              )}
            </Box>
          )}
        </Paper>

        <Paper sx={{ p: 3 }}>
          <Typography variant="h6" gutterBottom>
            Registered Speakers
          </Typography>
          {Object.entries(speakers).map(([id, name]) => (
            <Typography key={id}>
              {name} (ID: {id})
            </Typography>
          ))}
        </Paper>
      </Box>
    </Container>
  );
}

export default App;
