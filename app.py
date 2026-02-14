import os
import uuid
import time
import random
import yt_dlp
from flask import Flask, request, send_file
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

DOWNLOAD_FOLDER = 'downloads'
if not os.path.exists(DOWNLOAD_FOLDER):
    os.makedirs(DOWNLOAD_FOLDER)

def cleanup_old_files():
    """সার্ভারের স্পেস বাঁচাতে ১০ মিনিটের বেশি পুরনো ফাইল মুছে ফেলে"""
    now = time.time()
    for f in os.listdir(DOWNLOAD_FOLDER):
        path = os.path.join(DOWNLOAD_FOLDER, f)
        if os.stat(path).st_mtime < now - 600:
            try: os.remove(path)
            except: pass

@app.route('/')
def home():
    return "Special 720p HD API is Running! (Supports MP3 & MP4)"

@app.route('/download', methods=['GET'])
def download_720p():
    cleanup_old_files()
    video_url = request.args.get('url')
    format_type = request.args.get('format', 'mp4')

    if not video_url:
        return "Error: Please provide a video URL.", 400

    unique_id = f"special_720p_{str(uuid.uuid4())[:8]}"
    
    # লেটেস্ট ইউজার এজেন্ট
    user_agents = [
        'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36',
        'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36'
    ]

    try:
        if format_type == 'mp3':
            # অডিওর জন্য হাই কোয়ালিটি সেটিংস
            ydl_opts = {
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
            }
        else:
            # ৭২০পি ভিডিও সেটিংস
            # এটি সর্বোচ্চ ৭২০পি নামাবে, না থাকলে তার নিচের সেরা কোয়ালিটি নেবে
            ydl_opts = {
                'format': 'bestvideo[height<=720][ext=mp4]+bestaudio[ext=m4a]/best[height<=720][ext=mp4]/best',
                'merge_output_format': 'mp4',
            }

        # ইউনিভার্সাল সেটিংস (সব প্লাটফর্মের জন্য)
        ydl_opts.update({
            'outtmpl': f'{DOWNLOAD_FOLDER}/{unique_id}.%(ext)s',
            'user_agent': random.choice(user_agents),
            'geo_bypass': True,
            'nocheckcertificate': True,
            'quiet': True,
            'no_warnings': True,
            'noplaylist': True,
        })

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(video_url, download=True)
            filename = ydl.prepare_filename(info)
            
            # MP3 এক্সটেনশন ফিক্স
            if format_type == 'mp3':
                filename = os.path.splitext(filename)[0] + '.mp3'
            
            return send_file(filename, as_attachment=True)

    except Exception as e:
        return f"Server Error: {str(e)}", 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
