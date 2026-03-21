import subprocess






#PIPER_PATH = "./piper/piper"
PIPER_PATH = "/home/timothy/Desktop/Agentic_AI/sound_processing/piper/piper"
MODEL_PATH =  "/home/timothy/Desktop/Agentic_AI/sound_processing/en_US-lessac-medium.onnx"

def speak(text):
    print(f"Speaking {text}")

    command = f'echo "{text}" | {PIPER_PATH} --model {MODEL_PATH} --output_raw | aplay -r 22050 -f S16_LE -t raw -c 1 -D plughw:0,0'

    subprocess.run(command, shell=True)

example_text = "Hello, my name is Timothy Grant"
speak(example_text)