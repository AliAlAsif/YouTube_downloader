import yt_dlp
import os
import re
from urllib.parse import urlparse, parse_qs

def is_valid_youtube_url(url):
    youtube_regex = re.compile(r'(https?://)?(www\.)?(youtube|youtu|youtube-nocookie)\.(com|be)/(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})')
    match = youtube_regex.match(url)
    return bool(match)

def clean_video_url(url):
    parsed_url = urlparse(url)
    query_params = parse_qs(parsed_url.query)
    video_id = query_params.get('v')
    if video_id:
        return f"https://www.youtube.com/watch?v={video_id[0]}"
    return url

def download_video(video_url, download_path, cookies_path=None, fast=False):
    try:
        video_url = clean_video_url(video_url)

        ydl_opts = {
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'noplaylist': True,  # Ensure only the specific video is downloaded
            'quiet': True if fast else False,  # Reduce verbosity in fast mode
        }

        if cookies_path:
            ydl_opts['cookiefile'] = cookies_path

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # If fast download is selected, download the best available quality
            if fast:
                ydl_opts['format'] = 'best'  # Automatically download the best available video+audio stream
                print("\nFast download selected. Downloading best available quality...\n")
                ydl.download([video_url])
            else:
                # Fetch video information and available formats for manual selection
                info_dict = ydl.extract_info(video_url, download=False)
                formats = info_dict.get('formats', [])

                # Display all available formats for the user to choose
                print("\nAvailable Video Streams:")
                for i, fmt in enumerate(formats):
                    if fmt.get('vcodec') != 'none':  # Filter out audio-only formats
                        size = fmt.get('filesize_approx', 0)
                        print(f"{i + 1}. Resolution: {fmt.get('height')}p - FPS: {fmt.get('fps')} - Format ID: {fmt.get('format_id')} - Size: {size / (1024 * 1024):.2f} MB" if size else f"{i + 1}. Resolution: {fmt.get('height')}p - FPS: {fmt.get('fps')} - Format ID: {fmt.get('format_id')}")

                # Let the user select the preferred format
                stream_number = int(input("\nEnter the number of the stream you want to download: "))
                selected_format = formats[stream_number - 1]['format_id']
                ydl_opts['format'] = selected_format

                # Download the selected format
                print("\nDownloading...")
                ydl.download([video_url])

        print(f"Download completed! Video saved to {download_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

def download_audio(video_url, download_path, cookies_path=None, fast=False):
    try:
        video_url = clean_video_url(video_url)
        ydl_opts = {
            'format': 'bestaudio/best',
            'outtmpl': os.path.join(download_path, '%(title)s.%(ext)s'),
            'postprocessors': [{
                'key': 'FFmpegExtractAudio',
                'preferredcodec': 'mp3',
                'preferredquality': '192',
            }],
            'noplaylist': True,
            'quiet': True if fast else False,
        }

        if fast:
            ydl_opts['concurrent_fragments'] = 5  # Speed up by downloading multiple fragments concurrently

        if cookies_path:
            ydl_opts['cookiefile'] = cookies_path

        print("\nDownloading...")
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            ydl.download([video_url])
        print(f"Download completed! Audio saved to {download_path}")

    except Exception as e:
        print(f"An error occurred: {e}")

def main():
    while True:
        print("\nYouTube Video Downloader 🖥️🔓")
        print("1. Download Video")
        print("2. Download Audio Only")
        print("3. Exit")
        choice = input("\nEnter your choice: ")

        if choice == '1' or choice == '2':
            video_url = input("\nEnter the YouTube video URL: ")
            while not is_valid_youtube_url(video_url):
                print("\nInvalid YouTube URL. Please enter a valid YouTube link.")
                video_url = input("\nEnter the YouTube video URL: ")

            download_path = input("\nEnter the download path (leave blank for current directory): ") or os.getcwd()
            cookies_path = input("\nEnter the path to your cookies.txt file (leave blank if not needed): ")
            fast_download = input("\nDo you want a fast download? (y/n): ").strip().lower() == 'y'

            if choice == '1':
                download_video(video_url, download_path, cookies_path if cookies_path else None, fast_download)
            elif choice == '2':
                download_audio(video_url, download_path, cookies_path if cookies_path else None, fast_download)
        elif choice == '3':
            print("\nExiting...")
            break
        else:
            print("\nInvalid choice! Please select a valid option.")

if __name__ == "__main__":
    main()
