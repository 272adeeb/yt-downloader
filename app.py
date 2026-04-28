from flask import Flask, request, jsonify, send_file, send_from_directory, make_response
from flask_cors import CORS
import yt_dlp, os

app = Flask(__name__)
CORS(app, origins="*", supports_credentials=False)

DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

FORMAT_MAP = {
    'best':  'best[ext=mp4]/best',
    '720p':  'best[height<=720][ext=mp4]/best[height<=720]',
    '480p':  'best[height<=480][ext=mp4]/best[height<=480]',
    'audio': 'bestaudio/best',
}

@app.after_request
def add_cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type'
    response.headers['Access-Control-Allow-Methods'] = 'POST, GET, OPTIONS'
    return response

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/privacy')
def privacy():
    return send_from_directory('.', 'privacy.html')

@app.route('/download', methods=['POST', 'OPTIONS'])
def download():
    if request.method == 'OPTIONS':
        return make_response('', 204)

    data = request.get_json()
    url = data.get('url', '').strip()
    quality = data.get('quality', 'best')

    if not url:
        return jsonify({'error': 'Please enter a URL'}), 400

    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'format': FORMAT_MAP.get(quality, FORMAT_MAP['best']),
        'noplaylist': True,
        'quiet': True,
        'nocheckcertificate': True,
        'legacy_server_connect': True,
        'retries': 10,
        'fragment_retries': 10,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'video')
            filename = ydl.prepare_filename(info)
            if quality == 'audio':
                filename = os.path.splitext(filename)[0] + '.mp3'
            basename = os.path.basename(filename)
            return jsonify({'filename': basename, 'title': title})
    except Exception as e:
        return jsonify({'error': str(e)}), 400

@app.route('/file/<path:filename>')
def serve_file(filename):
    return send_file(
        os.path.join(DOWNLOAD_FOLDER, filename),
        as_attachment=True
    )

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)
