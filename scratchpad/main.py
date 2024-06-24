import pydub

audio = pydub.AudioSegment.from_mp3('let-her-go.mp3')
partial = audio[:1000]
print(dir(partial))
print(partial)
