from flask import Flask, send_file, jsonify, abort, Response
import os
import librosa
import numpy as np
import matplotlib.pyplot as plt
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

app = Flask(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))
MEDIA_DIR = os.path.join(CURRENT_DIR, 'Audio')

# Dictionary to store file IDs
file_ids = {}

@app.route('/media_files')
def list_media_files():
    try:
        files = []
        for index, f in enumerate(os.listdir(MEDIA_DIR)):
            if f.endswith('.mp3'):
                file_id = index + 1
                file_ids[file_id] = f
                base_name = os.path.splitext(f)[0]
                files.append({
                    'id': file_id,
                    'name': f,
                    'title': base_name,
                    'image': f'get_cover/{file_id}',
                    'path': f'get_mp3/{file_id}',
                    'waveform': f'get_waveform/{file_id}'
                })
        return jsonify(files)
    except Exception as e:
        return str(e), 500

@app.route('/')
def init():
    return "Music Player Python Backend"

@app.route('/get_mp3/<int:file_id>')
def get_mp3(file_id):
    filename = file_ids.get(file_id)
    if filename:
        file_path = os.path.join(MEDIA_DIR, filename)
        if os.path.isfile(file_path):
            try:
                return send_file(file_path, mimetype='audio/mpeg')
            except Exception as e:
                return str(e), 500
        else:
            abort(404)
    else:
        abort(404)

@app.route('/get_name/<int:file_id>')
def get_name(file_id):
    filename = file_ids.get(file_id)
    if filename:
        return jsonify({'id': file_id, 'name': filename})
    else:
        abort(404)
@app.route('/get_cover/<int:file_id>')
def get_cover(file_id):
    filename = file_ids.get(file_id)
    if filename:
        file_path = os.path.join(MEDIA_DIR, filename)
        if os.path.isfile(file_path):
            try:
                audio = MP3(file_path, ID3=ID3)
                for tag in audio.tags.values():
                    if isinstance(tag, APIC):
                        return Response(tag.data, mimetype=tag.mime)
                return abort(404)
            except Exception as e:
                return str(e), 500
        else:
            abort(404)
    else:
        abort(404)

@app.route('/get_waveform/<int:file_id>')
def get_waveform(file_id):
    filename = file_ids.get(file_id)
    if filename:
        file_path = os.path.join(MEDIA_DIR, filename)
        if os.path.isfile(file_path):
            try:
                # Load audio file
                y, sr = librosa.load(file_path)
                # Compute the RMS (Root Mean Square) energy for the audio
                rms = librosa.feature.rms(y=y)
                # Normalize RMS to [0, 1]
                rms /= np.max(rms)
                # Calculate duration of the audio in seconds
                duration = librosa.get_duration(y=y, sr=sr)
                # Calculate number of samples needed (one per 200ms)
                num_samples = 200
                # Resample RMS to match the number of samples
                waveform_resampled = np.interp(
                    np.linspace(0, len(rms[0]) - 1, num_samples),
                    range(len(rms[0])),
                    rms[0]
                )
                # Scale to [1, 100]
                waveform_scaled = waveform_resampled * 99 + 1
                return jsonify(waveform_scaled.tolist())
            except Exception as e:
                return str(e), 500
        else:
            abort(404)
    else:
        abort(404)

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
