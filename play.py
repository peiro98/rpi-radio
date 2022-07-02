import struct
import wave
import pyaudio

sink = pyaudio.PyAudio()
sink = sink.open(format=pyaudio.paInt16, channels=2, rate=44100, output=True)

wav_file = wave.open("lofi.wav", "r")

print(f"Sample rate: {wav_file.getframerate()}")
print(f"Channels: {wav_file.getnchannels()}")
print(f"Sample width: {wav_file.getsampwidth()}")
print(f"Num of frames: {wav_file.getnframes()}")

data = wav_file.readframes(1024)
while len(data) > 0:
    sink.write(data)
    data = wav_file.readframes(1024)
