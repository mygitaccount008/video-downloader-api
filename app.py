from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import subprocess
from werkzeug.utils import secure_filename

app = Flask(__name__)

# WARNING: Only download content you own or have permission to download!
# YouTube Terms prohibit downloading unless a download button is provided.

@app.route('/')
def home():
    return '''<h1>Video Downloader API</h1>
    <p><strong>WARNING:</strong> Only download content you own or have permission to download.</p>
    <p>YouTube Terms of Service PROHIBIT downloading unless YouTube provides a download feature.</p>
    <h2>Usage:</h2>
    <p>GET /download?url=YOUR_VIDEO_URL</p>
    <p>Example: /download?url=https://www.youtube.com/watch?v=VIDEO_ID</p>
    '''

@app.route('/download')
def download():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({'error': 'No URL provided. Use ?url=VIDEO_URL'}), 400
    
    try:
        # Create temp directory
        output_dir = '/tmp'
        
        ydl_opts = {
            'format': 'bv*+ba/best',
            'merge_output_format': 'mp4',
            'outtmpl': os.path.join(output_dir, '%(title).200B-%(id)s.%(ext)s'),
            'noplaylist': True,
            'restrictfilenames': True,
            'quiet': True,
        }
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
        
        # Send file to user
        return send_file(
            filename,
            as_attachment=True,
            download_name=os.path.basename(filename)
        )
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    # Install ffmpeg on start
    try:
        subprocess.run(['apt-get', 'update'], check=True, capture_output=True)
        subprocess.run(['apt-get', 'install', '-y', 'ffmpeg'], check=True, capture_output=True)
    except:
        pass
    
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
