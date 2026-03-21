import subprocess






PIPER_PATH = "./piper/piper"
MODEL_PATH =  "en_US-lessac-medium.onnx"

def speak(text):
    print(f"Speaking {text}")

    command = f'echo "{text}" | {PIPER_PATH} --model {MODEL_PATH} --output_raw | aplay -r 22050 -f S16_LE -t raw -D hw:0,0'

    subprocess.run(command, shell=True)