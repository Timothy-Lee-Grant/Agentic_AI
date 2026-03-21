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
input_device_index = None

def get_usb_device_index():
    global input_device_index
    p = pyaudio.PyAudio()
    for i in range(p.get_device_count()):
        dev = p.get_device_info_by_index(i)
        if "USB Audio" in dev['name'] or "P10S" in dev['name']:
            p.terminate()
            input_device_index = i
            return i
    p.terminate()
    return None

def record_audio():
    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS, rate=RATE,
                        input=True, input_device_index=input_device_index , frames_per_buffer=CHUNK)
    
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
    # 1. Create a downsampled version for Whisper
    # -i: input, -ar: audio rate (16k), -y: overwrite if exists
    CONVERTED_WAVE = "input_16k.wav"
    convert_cmd = ["ffmpeg", "-i", WAVE_OUTPUT, "-ar", "16000", "-ac", "1", CONVERTED_WAVE, "-y"]
    subprocess.run(convert_cmd, capture_output=True)
    
    #call the C++ binary directly
    # -nt: no time stamps, -otxt: ouput just the text
    cmd = [WHISPER_PATH, "-m", MODEL_PATH, "-f", CONVERTED_WAVE, "-nt"]
    result = subprocess.run(cmd, capture_output=True, text=True)
    return result.stdout.strip()

if __name__ == "__main__":
    get_usb_device_index()
    record_audio()
    text = transcribe()
    print(f"you said {text}") 