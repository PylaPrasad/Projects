# main.py - Kivy version for Android using yt-dlp
# Changed from youtube_dl to yt_dlp for better maintenance and features,
# as specified in buildozer.spec requirements.

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.checkbox import CheckBox
from kivy.uix.spinner import Spinner
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.core.window import Window
import yt_dlp as youtube_dl # Import yt_dlp and alias it as youtube_dl for compatibility
import os
import threading
# If you need to access public storage (e.g., Downloads folder for user access),
# you would typically use pyjnius to interact with Android's Java APIs.
# For example:
# from jnius import autoclass
# Environment = autoclass('android.os.Environment')
# download_dir = Environment.getExternalStoragePublicDirectory(Environment.DIRECTORY_DOWNLOADS).getAbsolutePath()
# For simplicity in this example, we keep it in app's user data directory.

Window.size = (400, 700) # Set the initial window size for the Kivy app

class DownloaderLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        self.audio_only = False
        # Define output directory within the app's private data space.
        # For public storage, see comments above.
        self.output_dir = os.path.join(App.get_running_app().user_data_dir, "downloads")
        os.makedirs(self.output_dir, exist_ok=True) # Ensure the downloads directory exists

        # UI elements
        self.add_widget(Label(text='Enter YouTube URLs (one per line):', font_size='18sp', bold=True))
        self.url_input = TextInput(multiline=True, size_hint_y=0.3, hint_text='Paste URLs here...')
        self.add_widget(self.url_input)

        self.audio_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=40, spacing=5)
        self.audio_checkbox = CheckBox(size_hint_x=None, width=40)
        self.audio_checkbox.bind(active=self.on_audio_toggle)
        self.audio_layout.add_widget(self.audio_checkbox)
        self.audio_layout.add_widget(Label(text='Audio Only (MP3/M4A/WebM)', font_size='16sp'))
        self.add_widget(self.audio_layout)

        self.audio_spinner = Spinner(text='mp3', values=('mp3', 'm4a', 'webm'), size_hint_y=None, height=50,
                                     option_cls=Label) # Add option_cls for spinner styling
        self.add_widget(self.audio_spinner)

        self.download_button = Button(text='Start Download', size_hint_y=None, height=60,
                                      font_size='20sp', background_normal='', background_color=(0.2, 0.6, 1, 1))
        self.download_button.bind(on_press=self.start_download_thread)
        self.add_widget(self.download_button)

        self.progress = ProgressBar(max=100, value=0, size_hint_y=None, height=30)
        self.add_widget(self.progress)

        self.status_label = Label(text='Status: Ready', size_hint_y=None, height=40, font_size='16sp')
        self.add_widget(self.status_label)

        self.log_output = TextInput(readonly=True, size_hint_y=0.3, background_color=(0.1, 0.1, 0.1, 1),
                                    foreground_color=(1, 1, 1, 1), font_name='RobotoMono', font_size='12sp')
        self.add_widget(self.log_output)

    def on_audio_toggle(self, checkbox, value):
        """Toggles the audio_only flag based on checkbox state."""
        self.audio_only = value
        self.audio_spinner.disabled = not value # Disable spinner if audio_only is false

    def start_download_thread(self, instance):
        """Initiates the download in a separate thread to keep the UI responsive."""
        urls = self.url_input.text.strip().splitlines()
        if not urls or all(not url.strip() for url in urls):
            Clock.schedule_once(lambda dt: self.status_label.setter('text')(self.status_label, "❌ No URLs entered."))
            return

        self.download_button.disabled = True
        self.progress.value = 0
        self.log_output.text = "" # Clear previous logs
        Clock.schedule_once(lambda dt: self.status_label.setter('text')(self.status_label, "Starting downloads..."))
        threading.Thread(target=self.download_all, daemon=True).start()

    def download_all(self):
        """Iterates through all entered URLs and downloads them."""
        urls = [url.strip() for url in self.url_input.text.strip().splitlines() if url.strip()]
        total = len(urls)
        for idx, url in enumerate(urls):
            Clock.schedule_once(lambda dt: self.status_label.setter('text')(self.status_label, f"Downloading {idx+1}/{total}: {url[:40]}..."))
            self.download_video(url)
            # Update overall progress
            Clock.schedule_once(lambda dt: self.progress.setter('value')(self.progress, ((idx+1)/total)*100))
        Clock.schedule_once(lambda dt: self.status_label.setter('text')(self.status_label, "✅ All downloads completed."))
        Clock.schedule_once(lambda dt: setattr(self.download_button, 'disabled', False))

    def download_video(self, url):
        """Downloads a single video or audio using yt-dlp."""
        try:
            # yt-dlp options
            opts = {
                'quiet': True, # Suppress stdout messages from yt-dlp
                'progress_hooks': [self.yt_progress_hook], # Hook for progress updates
                # Output template. For simplicity, naming by title.
                # If you prefer playlist structure, adjust as needed.
                'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                'noplaylist': True, # Do not download playlists, only single videos
            }

            if self.audio_only:
                opts.update({
                    'format': 'bestaudio/best', # Get best audio format
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': self.audio_spinner.text, # Use selected audio format (mp3, m4a, webm)
                        'preferredquality': '192', # Audio quality
                    }],
                    # Output template for audio only, ensuring correct extension
                    'outtmpl': os.path.join(self.output_dir, '%(title)s.%(extractor)s.%(ext)s'),
                })
            else:
                opts.update({
                    'format': 'bestvideo+bestaudio/best', # Get best video and audio, then merge
                    'merge_output_format': 'mp4', # Merge into MP4 format
                })

            with youtube_dl.YoutubeDL(opts) as ydl:
                ydl.download([url])

        except youtube_dl.DownloadError as e:
            # Catch specific yt-dlp download errors for clearer messages
            Clock.schedule_once(lambda dt: self.log_output.insert_text(f"❌ Download Error for {url}: {str(e)}\n"))
        except Exception as e:
            # Catch any other general exceptions
            Clock.schedule_once(lambda dt: self.log_output.insert_text(f"❌ General Error for {url}: {str(e)}\n"))

    def yt_progress_hook(self, d):
        """Hook to update UI with download progress."""
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', 'N/A').strip()
            total_size = d.get('_total_bytes_str', 'N/A').strip()
            downloaded_bytes = d.get('downloaded_bytes', 0)
            total_bytes = d.get('total_bytes') or d.get('total_bytes_estimate', 0)
            
            # Calculate progress for current file more accurately if available
            current_progress = 0
            if total_bytes > 0:
                current_progress = (downloaded_bytes / total_bytes) * 100

            Clock.schedule_once(lambda dt: self.status_label.setter('text')(self.status_label, f"Downloading: {percent} ({total_size})"))
            # Note: This progress bar reflects the current file. The overall progress
            # is updated in download_all. You might want a separate bar for overall.
            # Clock.schedule_once(lambda dt: self.progress.setter('value')(self.progress, current_progress))
        elif d['status'] == 'finished':
            Clock.schedule_once(lambda dt: self.log_output.insert_text(f"✅ Finished: {d['filename']}\n"))
        elif d['status'] == 'error':
            Clock.schedule_once(lambda dt: self.log_output.insert_text(f"❌ Error during processing: {d.get('e', 'Unknown error')}\n"))


class YTApp(App):
    def build(self):
        """Builds the root widget for the Kivy application."""
        self.title = 'YouTube Downloader' # Set the application title
        return DownloaderLayout()

if __name__ == '__main__':
    YTApp().run()
