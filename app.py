from flask import Flask, request, render_template, send_file
import yt_dlp
import os
import shutil
from pydub import AudioSegment

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

def download_trim_and_merge_youtube_audio(urls, output_dir='downloads', max_songs=20, trim_duration=30):
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

    # Initialize an empty AudioSegment for merging
    combined_audio = AudioSegment.silent(duration=0)

    # Trimming and merging the audio files
    for file_name in os.listdir(output_dir):
        if file_name.endswith('.mp3'):
            file_path = os.path.join(output_dir, file_name)
            audio = AudioSegment.from_mp3(file_path)
            trimmed_audio = audio[:trim_duration * 1000]  # 30 seconds
            combined_audio += trimmed_audio

    # Export the merged audio
    combined_output_path = os.path.join(output_dir, 'merged_output.mp3')
    combined_audio.export(combined_output_path, format="mp3")

    return combined_output_path

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        search_query = request.form['search_query']
        max_songs = int(request.form['max_songs'])
        
        urls = search_youtube(search_query, max_results=max_songs)
        combined_output_path = download_trim_and_merge_youtube_audio(urls, max_songs=max_songs)
        
        # Return the merged output file
        return send_file(combined_output_path, as_attachment=True)

    return render_template('index.html')

if __name__ == '__main__':
    app.run(debug=True)
