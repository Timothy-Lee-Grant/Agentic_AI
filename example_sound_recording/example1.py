import pyaudio
import wave
import subprocess
import os


FORMAT = pyaudio.paInt16
CHANNELS = 2
RATE = 48000
CHUNK = 1024
WAVE_OUTPUT = "input.wav"
WHISPER_PATH = "/home/timothy/Desktop/whisper.cpp/build/bin/whisper-cli"
MODEL_PATH = "/home/timothy/Desktop/whisper.cpp/models/ggml-base.bin"
 
def record_audio():
    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, input_device_index=24 , frames_per_buffer=CHUNK)
    
    print("Listening")
    frames = []

    try:
        while True:
            data = stream.read(CHUNK)
            frames.append(data)
    except KeyboardInterrupt:
        print("Finishing")
    
    with wave.open(WAVE_OUTPUT, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    
    stream.stop_stream()
    stream.close()
    audio.terminate()

def transcribe():
    #call the C++ binary directly
    # -nt: no time stamps, -otxt: ouput just the text
    cmd = [WHISPER_PATH, "-m", MODEL_PATH, "-f", WAVE_OUTPUT, "-nt"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

if __name__ == "__main__":
    record_audio()
    text = transcribe()
    print(f"you said {text}") 