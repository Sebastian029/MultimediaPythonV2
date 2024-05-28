from flask import Flask, send_file, jsonify, abort, Response
import os
from mutagen.mp3 import MP3
from mutagen.id3 import ID3, APIC

app = Flask(__name__)

CURRENT_DIR = os.path.dirname(os.path.abspath(__file__))

MEDIA_DIR = os.path.join(CURRENT_DIR, 'Audio')

@app.route('/media_files')
def list_media_files():
    try:
        files = []
        for f in os.listdir(MEDIA_DIR):
            if f.endswith('.mp3'):
                base_name = os.path.splitext(f)[0]
                files.append({
                    'name': f,
                    'title': base_name,
                    'image': f'get_cover/{f}',
                    'path': f'get_mp3/{f}'
                })
        return jsonify(files)
    except Exception as e:
        return str(e), 500

@app.route('/')
def init():
    return "Music Player Python Backend"

@app.route('/get_mp3/<filename>')
def get_mp3(filename):
    file_path = os.path.join(MEDIA_DIR, filename)
    if os.path.isfile(file_path):
        try:
            return send_file(file_path, mimetype='audio/mpeg')
        except Exception as e:
            return str(e), 500
    else:
        abort(404)

@app.route('/get_cover/<filename>')
def get_cover(filename):
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

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)