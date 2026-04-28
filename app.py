from flask import Flask, request, jsonify, send_file, send_from_directory
import yt_dlp
import os

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

# Corrected variable name to match the function call
FORMAT_MAP = {
    'best':  'best[ext=mp4]/best',
    '720p':  'best[height<=720][ext=mp4]/best[height<=720]',
    '480p':  'best[height<=480][ext=mp4]/best[height<=480]',
    'audio': 'bestaudio/best',
}

@app.route('/')
def index():
    # Looks for 'index.html' in the same folder
    return send_from_directory('.', 'index.html')

@app.route('/download', methods=['POST'])
def download():
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
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            title = info.get('title', 'video')
            filename = ydl.prepare_filename(info)
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
    app.run(host='0.0.0.0', port=port)
