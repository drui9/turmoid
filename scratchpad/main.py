import speech_recognition as sr

r = sr.Recognizer()
with sr.AudioFile('speaker.wav') as source:
    audio = r.record(source)

key = 'GOOGLE_SPEECH_RECOGNITION_API_KEY'
text = sr.recognize_api(sr, audio_data=audio, client_access_token=key)
print(text)
