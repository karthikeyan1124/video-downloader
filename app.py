from flask import Flask, request, jsonify, send_from_directory, render_template_string
import os
import yt_dlp

app = Flask(__name__)

# Path for storing downloaded videos
DOWNLOAD_FOLDER = 'downloads'
STATIC_FOLDER = 'static'

if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)
if not os.path.exists(STATIC_FOLDER):
    os.makedirs(STATIC_FOLDER)

# Serve the frontend HTML
@app.route('/')
def home():
    with open('index1.html') as f:
        return render_template_string(f.read())

def download_video(url):
    try:
        output_path = DOWNLOAD_FOLDER
        options = {
             'outtmpl': f'{output_path}/%(title)s.%(ext)s',
            'format': 'bestvideo+bestaudio',
            'merge_output_format': 'mp4',  # Ensures video and audio are merged into MP4 format
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.159 Safari/537.36'
            }
        }

        with yt_dlp.YoutubeDL(options) as ydl:
            info = ydl.extract_info(url, download=True)
            filepath = os.path.join(output_path, f"{info['title']}.mp4")
            return filepath
    except yt_dlp.utils.DownloadError as e:
        if "ffmpeg" in str(e).lower():
            return "FFmpeg is not installed. Please install FFmpeg to enable video merging."
        return str(e)
    except Exception as e:
        return str(e)

@app.route('/download', methods=['POST'])
def download():
    data = request.get_json()
    url = data.get('url')

    if not url:
        return jsonify({"success": False, "error": "URL is required."})

    try:
        filepath = download_video(url)

        if not os.path.isfile(filepath):
            return jsonify({"success": False, "error": filepath})

        filename = os.path.basename(filepath)
        static_path = os.path.join(STATIC_FOLDER, filename)
        os.rename(filepath, static_path)

        download_url = f"/static/{filename}"

        return jsonify({"success": True, "download_url": download_url})
    except Exception as e:
        return jsonify({"success": False, "error": str(e)})

@app.route('/static/<path:filename>')
def serve_static(filename):
    return send_from_directory(STATIC_FOLDER, filename)

if __name__ == '__main__':
    app.run(debug=True)
