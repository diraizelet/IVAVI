
# # -*- coding: utf-8 -*-
# """audiotest.ipynb

# Automatically generated by Colab.

# Original file is located at
#     https://colab.research.google.com/drive/181hvmXQrdB6XazzUSYsNuU0oPSMeOSrS
# """

# !pip install SpeechRecognition
# !pip install pydub
# # Install Kivy (Google Colab does not support GUI apps natively, so it's limited)
# !pip install kivy[full] kivy_examples

# # Install sounddevice and scipy for audio recording and processing
# !pip install sounddevice scipy

# # Install requests for making HTTP requests
# !pip install requests

# # Install soundfile for audio playback
# !pip install soundfile

# # Install Google Generative AI (make sure you have the API key for this)
# !pip install google-generative-ai

# # Install gTTS for text-to-speech conversion
# !pip install gtts

# # Install Pillow for image processing
# !pip install Pillow

# # Install PortAudio library
# !apt-get install -y portaudio19-dev

# # Install sounddevice library after PortAudio is installed
# !pip install sounddevice

# !apt-get install ffmpeg

#process_the_data

from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.camera import Camera
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.core.image import Image as CoreImage
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
import sounddevice as sd
import numpy as np
import time
import os
from scipy.io.wavfile import write
from kivy.clock import Clock
import soundfile as sf  # For playing audio



def process_the_data(image, input_audio):
  question = wav_to_text(input_audio)
  response = backend(image,question)

  output_audio_path = text_to_speech(response)
  return output_audio_path

#INPUT TO ANSWER

import google.generativeai as genai
import PIL.Image

def backend(input_image, question):
  genai.configure(api_key="your gemini api key")

  img = PIL.Image.open(input_image)

  model = genai.GenerativeModel(model_name="gemini-1.5-flash")
  response = model.generate_content([question, img])
  return response.text

# INPUT AUDIO TO TEXT

import speech_recognition as sr
import os

# Input and output file paths
# input_file = 'input_audio.mp3'  # replace with your file
# output_file = 'converted_output.wav'

# Convert the audio to PCM WAV format
#os.system(f"ffmpeg -i {input_file} -ar 16000 -ac 1 {output_file}")


def wav_to_text(wav_file):
    os.system(f"ffmpeg -i {wav_file} -ar 16000 -ac 1 {"converted_output.wav"}")
    # Initialize recognizer
    recognizer = sr.Recognizer()
    # Load the WAV file
    with sr.AudioFile("converted_output.wav") as source:
        audio_data = recognizer.record(source)
    try:
        # Recognize the audio using Google Web Speech API
        text = recognizer.recognize_google(audio_data)
        print("Text: " + text)
        return text
    except sr.UnknownValueError:
        print("Google Speech Recognition could not understand the audio")
    except sr.RequestError as e:
        print(f"Could not request results from Google Speech Recognition service; {e}")

#OUTPUT TO VOICE MODULE
from gtts import gTTS
def text_to_speech(text, filename="output.wav"):
    try:
        # Create a gTTS object
        tts = gTTS(text=text, lang='en')

        # Save the converted audio to a file
        tts.save(filename)

        # Play the audio file
        #os.system(f"start {filename}")  # For Windows
        # os.system(f"afplay {filename}")  # For macOS
        # os.system(f"xdg-open {filename}")  # For Linux
        output_audio_path=filename
        print(f"Audio saved and played: {filename}")

    except Exception as e:
        print(f"An error occurred: {e}")
    return filename

image_path = ""
audio_path = ""
output_audio_path = ""



#main screen that opens to the camera directly



#APP FRONTEND TO RUN THE AUDIO RECORDING SCREEN

class AudioRecordingScreen(Screen):
    def __init__(self, **kwargs):
        super(AudioRecordingScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        self.timer_label = Label(text="00:00:00", font_size='24sp', size_hint=(1, 0.1))
        layout.add_widget(self.timer_label)

        self.record_button = Button(size_hint=(None, None), size=(200, 200), pos_hint={'center_x': 0.5, 'center_y': 0.5}, background_color=(0, 1, 0, 1))
        self.record_button.bind(on_press=self.toggle_recording)
        layout.add_widget(self.record_button)

        self.add_widget(layout)
        self.recording = False
        self.audio_data = []
        self.fs = 44100  # Sampling frequency
        self.stream = None
        self.recording_start_time = None

    def toggle_recording(self, instance):
        if self.recording:
            self.stop_recording()
        else:
            self.start_recording()

    def start_recording(self):
        if not self.recording:
            self.recording = True
            self.record_button.background_color = (1, 0, 0, 1)  # Change color to red
            self.recording_start_time = time.time()
            self.audio_data = []
            self.stream = sd.InputStream(samplerate=self.fs, channels=1, callback=self.audio_callback)
            try:
                self.stream.start()
                self.update_timer()
                print("Recording started...")
            except Exception as e:
                print(f"Error starting stream: {e}")

    def stop_recording(self):
        global audio_path, output_audio_path  # Use global to access the variables
        if self.recording:
            self.recording = False
            self.record_button.background_color = (0, 1, 0, 1)  # Change color to green
            if self.stream:
                self.stream.stop()
                self.stream.close()
            filename = self.save_recording()
            duration = time.time() - self.recording_start_time
            print(f"Audio saved as {filename} with duration {duration:.2f} seconds")
            self.timer_label.text = f"Duration: {duration:.2f} seconds"
            audio_path = filename  # Set the correct path
             # Get the output audio file path

             #now process the backend
            output_audio_path = process_the_data(image_path,audio_path)
            self.manager.current = 'audio_playback'  # Move to the playback screen

    def audio_callback(self, indata, frames, time, status):
        if status:
            print(f"Audio callback status: {status}")
        if self.recording:
            self.audio_data.append(indata.copy())

    def save_recording(self):
        directory = 'audio'
        if not os.path.exists(directory):
            os.makedirs(directory)

        timestamp = time.strftime("%Y%m%d_%H%M%S")
        filename = os.path.join(directory, f"audio_{timestamp}.wav")
        audio_array = np.concatenate(self.audio_data, axis=0)
        write(filename, self.fs, audio_array)

        return filename

    def update_timer(self):
        if self.recording:
            elapsed_time = time.time() - self.recording_start_time
            minutes, seconds = divmod(int(elapsed_time), 60)
            hours, minutes = divmod(minutes, 60)
            self.timer_label.text = f"{hours:02}:{minutes:02}:{seconds:02}"
            Clock.schedule_once(lambda dt: self.update_timer(), 1)

#THE PAGE THAT PLAYS THE AUDIO RETURNED AS A ANSWER
class AudioPlaybackScreen(Screen):
    def __init__(self, **kwargs):
        super(AudioPlaybackScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')

        # Add a button to play the output audio
        self.play_button = Button(text="Play Audio", size_hint=(1, 0.2))
        self.play_button.bind(on_press=self.play_audio)
        layout.add_widget(self.play_button)

        # Add a back button to delete files and return to the camera screen
        self.back_button = Button(text="Back", size_hint=(1, 0.2))
        self.back_button.bind(on_press=self.delete_files_and_return)
        layout.add_widget(self.back_button)

        self.add_widget(layout)
        self.output_audio_path = None

    def set_output_audio_path(self, path):
        self.output_audio_path = path

    def play_audio(self, instance):
        if output_audio_path and os.path.exists(output_audio_path):
            # Play the audio using sounddevice
            audio_data, fs = sf.read(output_audio_path)
            sd.play(audio_data, fs)
            sd.wait()
        else:
            print("No audio file found to play.")

    def delete_files_and_return(self, instance):
        global image_path, audio_path, output_audio_path

        # Delete the files if they exist
        for file_path in [image_path, audio_path, self.output_audio_path]:
            if file_path and os.path.exists(file_path):
                os.remove(file_path)
                print(f"Deleted file: {file_path}")

        # Reset paths
        image_path = ""
        audio_path = ""
        self.output_audio_path = None

        # Return to the camera screen
        self.manager.current = 'main'

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super(MainScreen, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        self.camera = Camera(resolution=(640, 480), play=True, size_hint=(1, 0.8))
        self.label = Label(text='IVAVI', font_size='48sp', size_hint=(1, 0.2))
        layout.add_widget(self.camera)
        layout.add_widget(self.label)
        self.add_widget(layout)
        self.bind(on_touch_down=self.take_photo)

    def take_photo(self, instance, touch):
        global image_path  # Use global to access the variable
        if touch.is_double_tap:
            texture = self.camera.texture
            if texture:
                try:
                    img = CoreImage(texture, ext='png')
                    directory = 'photos'
                    if not os.path.exists(directory):
                        os.makedirs(directory)

                    timestamp = time.strftime("%Y%m%d_%H%M%S")
                    filename = os.path.join(directory, f"photo_{timestamp}.png")

                    img.save(filename)
                    print(f"Photo saved as {filename}")
                    image_path = filename  # Set the correct path
                    self.manager.current = 'audio_recording'
                except Exception as e:
                    print(f"Error saving photo: {e}")
            else:
                print("No texture available from the camera.")

class MyApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(AudioRecordingScreen(name='audio_recording'))
        sm.add_widget(AudioPlaybackScreen(name='audio_playback'))  # Add playback screen
        return sm


if __name__ == '__main__':
    MyApp().run()