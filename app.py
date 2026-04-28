from flask import Flask, request, jsonify, send_file, send_from_directory
import yt_dlp, os

app = Flask(__name__)
DOWNLOAD_FOLDER = 'downloads'
os.makedirs(DOWNLOAD_FOLDER, exist_ok=True)

@app.route('/')
def index():
    return send_from_directory('.', 'index.html')

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url', '').strip()
    quality = data.get('quality', 'best')

    if not url:
        return jsonify({'error': 'Please enter a URL'}), 400

    format_map = {
        'best':  'bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best',
        '720p':  'bestvideo[height<=720][ext=mp4]+bestaudio/best[height<=720]',
        '480p':  'bestvideo[height<=480][ext=mp4]+bestaudio/best[height<=480]',
        'audio': 'bestaudio/best',
    }

    ydl_opts = {
        'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
        'format': format_map.get(quality, format_map['best']),
        'noplaylist': True,
        'quiet': True,
        'nocheckcertificate': True,
        ydl_opts = {
    'outtmpl': f'{DOWNLOAD_FOLDER}/%(title)s.%(ext)s',
    'format': format_map.get(quality, format_map['best']),
    'noplaylist': True,
    'quiet': True,
    'nocheckcertificate': True,
    'extractor_args': {
        'youtube': {
            'player_client': ['android', 'web'],
        }
    },
    'legacy_server_connect': True,
    'retries': 10,
    'fragment_retries': 10,
    'retry_sleep_functions': {'http': lambda n: 3},
}

'legacy_server_connect': True,
'retries': 10,
'fragment_retries': 10,
'retry_sleep_functions': {'http': lambda n: 3},
    }

    if quality == 'audio':
        ydl_opts['postprocessors'] = [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }]

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
