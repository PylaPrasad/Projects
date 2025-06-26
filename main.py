# main.py - Kivy version for Android using youtube_dl

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
import youtube_dl
import os
import threading

Window.size = (400, 700)

class DownloaderLayout(BoxLayout):
    def __init__(self, **kwargs):
        super().__init__(orientation='vertical', padding=10, spacing=10, **kwargs)

        self.audio_only = False
        self.output_dir = os.path.join(App.get_running_app().user_data_dir, "downloads")
        os.makedirs(self.output_dir, exist_ok=True)

        self.add_widget(Label(text='Enter YouTube URLs (one per line):'))
        self.url_input = TextInput(multiline=True, size_hint_y=0.3)
        self.add_widget(self.url_input)

        self.audio_layout = BoxLayout(orientation='horizontal', size_hint_y=None, height=30)
        self.audio_checkbox = CheckBox()
        self.audio_checkbox.bind(active=self.on_audio_toggle)
        self.audio_layout.add_widget(self.audio_checkbox)
        self.audio_layout.add_widget(Label(text='Audio Only'))
        self.add_widget(self.audio_layout)

        self.audio_spinner = Spinner(text='mp3', values=('mp3', 'm4a', 'webm'), size_hint_y=None, height=40)
        self.add_widget(self.audio_spinner)

        self.download_button = Button(text='Start Download', size_hint_y=None, height=50)
        self.download_button.bind(on_press=self.start_download_thread)
        self.add_widget(self.download_button)

        self.progress = ProgressBar(max=100, value=0)
        self.add_widget(self.progress)

        self.status_label = Label(text='Status: Ready', size_hint_y=None, height=30)
        self.add_widget(self.status_label)

        self.log_output = TextInput(readonly=True, size_hint_y=0.3)
        self.add_widget(self.log_output)

    def on_audio_toggle(self, checkbox, value):
        self.audio_only = value

    def start_download_thread(self, instance):
        self.download_button.disabled = True
        self.progress.value = 0
        threading.Thread(target=self.download_all, daemon=True).start()

    def download_all(self):
        urls = self.url_input.text.strip().splitlines()
        total = len(urls)
        for idx, url in enumerate(urls):
            Clock.schedule_once(lambda dt: self.status_label.setter('text')(self.status_label, f"Downloading {idx+1}/{total}"))
            self.download_video(url.strip())
            Clock.schedule_once(lambda dt: self.progress.setter('value')(self.progress, ((idx+1)/total)*100))
        Clock.schedule_once(lambda dt: self.status_label.setter('text')(self.status_label, "✅ All downloads completed."))
        Clock.schedule_once(lambda dt: setattr(self.download_button, 'disabled', False))

    def download_video(self, url):
        try:
            opts = {
                'quiet': True,
                'progress_hooks': [self.yt_progress_hook],
                'outtmpl': os.path.join(self.output_dir, '%(playlist_title)s/%(playlist_index)s - %(title)s.%(ext)s'),
            }

            if self.audio_only:
                opts.update({
                    'format': 'bestaudio/best',
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': self.audio_spinner.text,
                        'preferredquality': '192',
                    }],
                    'outtmpl': os.path.join(self.output_dir, '%(title)s.%(ext)s'),
                })
            else:
                opts.update({
                    'format': 'best',
                    'merge_output_format': 'mp4',
                })

            with youtube_dl.YoutubeDL(opts) as ydl:
                ydl.download([url])

        except Exception as e:
            Clock.schedule_once(lambda dt: self.log_output.insert_text(f"❌ Error: {str(e)}\n"))

    def yt_progress_hook(self, d):
        if d['status'] == 'downloading':
            percent = d.get('_percent_str', '0%').strip()
            Clock.schedule_once(lambda dt: self.status_label.setter('text')(self.status_label, f"Downloading: {percent}"))
        elif d['status'] == 'finished':
            Clock.schedule_once(lambda dt: self.log_output.insert_text(f"✅ Finished: {d['filename']}\n"))

class YTApp(App):
    def build(self):
        return DownloaderLayout()

if __name__ == '__main__':
    YTApp().run()
