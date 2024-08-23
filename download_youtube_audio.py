from flask import Flask, request, render_template, send_file, jsonify
import yt_dlp
import os
import shutil

app = Flask(__name__)

def search_youtube(query, max_results=20):
    ydl_opts = {
        'default_search': 'ytsearch',
        'max_downloads': max_results,
        'quiet': True,
        'skip_download': True,
        'format': 'bestaudio/best',
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        search_result = ydl.extract_info(f"ytsearch{max_results}:{query}", download=False)
        return [entry['webpage_url'] for entry in search_result['entries']]

def download_youtube_audio(urls, output_dir='downloads', max_songs=20):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

    ydl_opts = {
        'format': 'bestaudio/best',
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
        'outtmpl': os.path.join(output_dir, '%(title)s.%(ext)s'),
    }

    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download(urls[:max_songs])

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_query = request.form['search_query']
        max_songs = int(request.form['max_songs'])
        
        urls = search_youtube(search_query, max_results=max_songs)
        download_youtube_audio(urls, max_songs=max_songs)
        
        # Returning the download directory as a zip file
        shutil.make_archive('downloads', 'zip', 'downloads')
        return send_file('downloads.zip', as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
