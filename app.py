from flask import Flask, request, send_file, jsonify
import yt_dlp
import os
import subprocess
from werkzeug.utils import secure_filename
import time

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
    <h3>Tips for YouTube:</h3>
    <ul>
        <li>API uses enhanced headers and cookies to bypass bot protection</li>
        <li>May work better during off-peak hours</li>
        <li>Some videos may still be restricted</li>
    </ul>
    '''

@app.route('/download')
def download():
    video_url = request.args.get('url')
    
    if not video_url:
        return jsonify({'error': 'No URL provided. Use ?url=VIDEO_URL'}), 400
    
    try:
        # Create temp directory
        output_dir = '/tmp'
        
        # Enhanced yt-dlp options to bypass bot protection
        ydl_opts = {
            'format': 'best[ext=mp4]/best',  # Get best single format
            'outtmpl': os.path.join(output_dir, '%(title).200B-%(id)s.%(ext)s'),
            'noplaylist': True,
            'restrictfilenames': True,
            'quiet': False,
            'no_warnings': False,
            # Enhanced headers to mimic real browser
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                'Accept-Language': 'en-us,en;q=0.5',
                'Sec-Fetch-Mode': 'navigate',
            },
            # Additional options to avoid detection
            'extractor_args': {'youtube': {'player_client': ['android', 'web']}},
            'sleep_interval': 1,
            'max_sleep_interval': 3,
        }
        
        print(f"Attempting to download: {video_url}")
        
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
        
        # Check if file exists
        if not os.path.exists(filename):
            return jsonify({'error': 'Download failed - file not created'}), 500
        
        print(f"Download successful: {filename}")
        
        # Send file to user
        return send_file(
            filename,
            as_attachment=True,
            download_name=os.path.basename(filename)
        )
    
    except Exception as e:
        error_msg = str(e)
        print(f"Error: {error_msg}")
        
        # Provide helpful error messages
        if 'Sign in' in error_msg or 'bot' in error_msg.lower():
            return jsonify({
                'error': 'YouTube bot protection detected',
                'message': 'YouTube is blocking automated downloads. Try again later or use a different video.',
                'technical_error': error_msg
            }), 403
        elif 'Video unavailable' in error_msg:
            return jsonify({
                'error': 'Video not available',
                'message': 'The video may be private, deleted, or region-restricted.',
                'technical_error': error_msg
            }), 404
        else:
            return jsonify({
                'error': 'Download failed',
                'message': error_msg
            }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
