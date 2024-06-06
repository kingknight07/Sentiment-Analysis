import tkinter as tk
from tkinter import ttk, filedialog
import pyaudio
import wave
import speech_recognition as sr
from textblob import TextBlob
import pandas as pd
from ttkthemes import ThemedStyle

class SentimentAnalysisApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Sentiment Analysis App")
        self.style = ThemedStyle(root)
        self.style.set_theme("radiance")

        self.sentiment_label = ttk.Label(root, text="Sentiment:", font=("Helvetica", 16))
        self.sentiment_label.pack(pady=10)

        self.input_label = ttk.Label(root, text="Input Text:", font=("Helvetica", 14))
        self.input_label.pack()

        self.input_text = tk.Text(root, width=50, height=4, font=("Helvetica", 12))
        self.input_text.pack()

        self.analyze_button = ttk.Button(root, text="Analyze Text", command=self.analyze_text, style='TButton')
        self.analyze_button.pack(pady=10)

        self.audio_label = ttk.Label(root, text="Or Analyze Audio:", font=("Helvetica", 14))
        self.audio_label.pack()

        self.record_button = ttk.Button(root, text="Record Audio", command=self.record_audio, style='TButton')
        self.record_button.pack()

        self.analyze_audio_button = ttk.Button(root, text="Analyze Audio File", command=self.analyze_audio, style='TButton')
        self.analyze_audio_button.pack()

        self.clear_button = ttk.Button(root, text="Clear", command=self.clear_input, style='TButton')
        self.clear_button.pack(pady=10)

        # Load negative slang words from CSV
        self.negative_slang_words = self.load_negative_slang_words()

    def load_negative_slang_words(self):
        df = pd.read_csv('sl.csv')
        return set(df['Slang Word'].str.lower())

    def analyze_text(self):
        input_text = self.input_text.get("1.0", "end-1c")
        sentiment = self.perform_sentiment_analysis(input_text)
        self.display_sentiment(sentiment)

    def analyze_audio(self):
        audio_file = filedialog.askopenfilename(filetypes=[("Audio Files", "*.wav")])
        if audio_file:
            audio_text = self.convert_audio_to_text(audio_file)
            sentiment = self.perform_sentiment_analysis(audio_text)
            self.display_sentiment(sentiment)

    def record_audio(self):
        audio_file = "audio.wav"
        self.record_audio_to_file(audio_file)
        audio_text = self.convert_audio_to_text(audio_file)
        sentiment = self.perform_sentiment_analysis(audio_text)
        self.display_sentiment(sentiment)

    def record_audio_to_file(self, output_file, duration=5):
        p = pyaudio.PyAudio()
        stream = p.open(format=pyaudio.paInt16, channels=1, rate=16000, input=True, frames_per_buffer=1024)
        frames = []
        print("Recording audio...")
        for i in range(0, int(16000 / 1024 * duration)):
            data = stream.read(1024)
            frames.append(data)
        print("Finished recording.")
        stream.stop_stream()
        stream.close()
        p.terminate()

        wf = wave.open(output_file, 'wb')
        wf.setnchannels(1)
        wf.setsampwidth(p.get_sample_size(pyaudio.paInt16))
        wf.setframerate(16000)
        wf.writeframes(b''.join(frames))
        wf.close()

    def convert_audio_to_text(self, audio_file):
        r = sr.Recognizer()
        with sr.AudioFile(audio_file) as source:
            audio_data = r.record(source)
        try:
            text = r.recognize_google(audio_data)
            return text
        except sr.UnknownValueError:
            return "Audio could not be understood"
        except sr.RequestError as e:
            return f"Could not request results from Google Web Speech API: {e}"

    def perform_sentiment_analysis(self, text):
        # Check for negative slang words
        text_lower = text.lower()
        for word in self.negative_slang_words:
            if word in text_lower:
                return "Negative"

        blob = TextBlob(text)
        sentiment = blob.sentiment.polarity
        if sentiment > 0.1:
            return "Positive"
        elif sentiment < -0.1:
            return "Negative"
        else:
            return "Neutral"

    def display_sentiment(self, sentiment):
        self.sentiment_label.config(text=f"Sentiment: {sentiment}", font=("Helvetica", 16))

    def clear_input(self):
        self.input_text.delete("1.0", tk.END)

if __name__ == "__main__":
    root = tk.Tk()
    app = SentimentAnalysisApp(root)
    root.mainloop()
