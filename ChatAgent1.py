import ollama
import pyaudio
import wave
import subprocess
import os
#from pynput import keyboard
from sshkeyboard import listen_keyboard
import threading

PIPER_PATH = "/home/timothy/Desktop/Agentic_AI/sound_processing/piper/piper"
MODEL_PATH_PIPER =  "/home/timothy/Desktop/Agentic_AI/sound_processing/en_US-lessac-medium.onnx"

# Audio recording parameters
FORMAT = pyaudio.paInt16
CHANNELS = 2 
RATE = 48000
CHUNK = 1024
WAVE_OUTPUT = "input.wav"
WHISPER_PATH = "/home/timothy/Desktop/whisper.cpp/build/bin/whisper-cli"
MODEL_PATH = "/home/timothy/Desktop/whisper.cpp/models/ggml-base.bin"
input_device_index = None

def StatusOfLightsInRoom():
    """Returns the state of all the lights in the user's room. Takes no arguments"""
    return "All lights are currently on."

def TemperatureInRoom():
    """Returns the temperature inside the user's room. Takes no arguments"""
    return "20 degrees Celcius."

available_functions = {
    "StatusOfLightsInRoom": StatusOfLightsInRoom,
    "TemperatureInRoom": TemperatureInRoom
}

available_function_ptr = [StatusOfLightsInRoom, TemperatureInRoom]


#I don't quite feel comfortable with this change in the system prompt because this is explicitly telling the LLM what keywords to look out for. This is much more similar to programmatically using keywords to branch. 
#Instead, I should be using the LLM to determine intent of the question to see if it matches a tool.
tool_determiner_prompt_old = [{
        "role": "system",
        "content": """Determine if the user is asking or mentioning room conditions like 
        heat, cold, lighting. If they mention being hot or cold, use the Temperature tool. 
        If they mention being dark or bright, or lights, use the Lights tool."""
    },{
        "role": "user",
        "content": ""
    }]

tool_determiner_prompt = [{
    "role": "system",
    "content": """You are an intent classifier.
    1. If the user explicitly asks about room temperature or feeling hot/cold, use TemperatureInRoom.
    2. If the user explicitly asks about lights or brightness, use StatusOfLightsInRoom.
    3. If the user is just chatting, making small talk, or asking about your day, DO NOT use any tools. Just respond normally.
    
    Only use a tool if it is strictly necessary to answer the user's specific question."""
    },{
        "role": "user",
        "content": ""
    }]

#attempting to add information about [KNOWLEDGE BASE] which gives additional information
# this could possibly bias the llm towards strange things, but I will see....
messages = [{"role": "system",
             "content": """You are a friendly AI companion. Talk with the user in a happy and helpful way.
             If the user provides [KNOWLEDGE BASE] data, use it to give a specific answer.
             If knowledge base is given, respond to the user by telling them the information given."""}]


def speak(text):
    print(f"Speaking {text}")

    command = f'echo "{text}" | {PIPER_PATH} --model {MODEL_PATH_PIPER} --output_raw | aplay -r 22050 -f S16_LE -t raw -c 1 -D plughw:0,0'

    subprocess.run(command, shell=True)




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














recording = False
should_quit = False
stop_recording_event = threading.Event()

def record_audio_worker():
    #This function runs in the background thread
    audio = pyaudio.PyAudio()

    stream = audio.open(format=FORMAT, channels=CHANNELS,
                        rate=RATE, input=True, input_device_index=input_device_index,
                        frames_per_buffer=CHUNK)

    print("\n[REC] Recording... Speak now!")
    frames = []

    while not stop_recording_event.is_set():
        data = stream.read(CHUNK)
        frames.append(data)
    
    #clean up
    stream.stop_stream()
    stream.close()
    audio.terminate()

    #save to ssd
    with wave.open(WAVE_OUTPUT, 'wb') as wf:
        wf.setnchannels(CHANNELS)
        wf.setsampwidth(audio.get_sample_size(FORMAT))
        wf.setframerate(RATE)
        wf.writeframes(b''.join(frames))
    print("[REC] Saved to disk.")

def on_press(key):
    global recording, should_quit
    if hasattr(key, 'char') and key.char == 'q':
        print("Quitting")
        should_quit = True
        return False
    
    if key == keyboard.Key.space and not recording:
        print("Starting recording...")
        recording = True
        
        stop_recording_event.clear() #reset the 'switch' to off
        #start background worker
        threading.Thread(target=record_audio_worker).start()

def on_release(key):
    global recording
    if key == keyboard.Key.space:
        print("Stopping recording...")
        recording = False
        stop_recording_event.set() #flip the 'switch' to ON
        return False # Stops listener

def press(key):
    global recording, should_quit
    if key == "space" and not recording:
        recording = True
        stop_recording_event.clear()
        threading.Thread(target=record_audio_worker).start()
    elif key == "q":
        global should_quit
        should_quit = True
        from sshkeyboard import stop_listening
        stop_listening()

def release(key):
    global recording, should_quit
    if key == "space":
        recording = False
        stop_recording_event.set()
        from sshkeyboard import stop_listening
        stop_listening()


if __name__ == "__main__":
    os.system("stty -echo") # Turn off terminal echo
    try:
        get_usb_device_index()

        while True:
            #Wait for the user to initiate a speaking command and then get their audio and have them give another command that they are done recording. 
            #with keyboard.Listener(on_press=on_press, on_release=on_release) as listener:
            #    listener.join()
            listen_keyboard(on_press=press, on_release=release, sequential=False)
            if should_quit:
                break

            userInput = transcribe()

            if userInput.lower() in ['q', 'quit']: break

            #use LLM to determine if tool is required/helpful
            tool_determiner_prompt[1]["content"] = userInput
            tool_use_llm_response = ollama.chat(model='llama3.2', messages=tool_determiner_prompt, tools=available_function_ptr, keep_alive=-1)
            
            context_info = ""
            if tool_use_llm_response.message.tool_calls:
                for tool in tool_use_llm_response.message.tool_calls:
                    print(f"---- Thinking: I need to use {tool.function.name} ----")
                    functionToCall = available_functions[tool.function.name]
                    context_info += f"\n[KNOWLEDGE BASE] {functionToCall()}[/[KNOWLEDGE BASE]]"
            
            #semi-dirty message history which will contain 'tool' knowledge, but will not continue to be added to the clean message history
            if context_info:
                llm_payload = messages + [{"role":"user", "content":userInput + context_info}]
            else:
                llm_payload = messages + [{"role": "user", "content": userInput}]

            response = ollama.chat(model='llama3.2', messages=llm_payload) 

            messages.append({"role": "user", "content": userInput})
            messages.append(response.message)
            print(response.message.content)
            speak(response.message.content)
            # --- SLIDING WINDOW ---
            # Keep the system prompt (index 0) + the last 10 messages
            #if len(messages) > 11:
            #    messages = [messages[0]] + messages[-10:]
            # ----------------------
    finally:
        os.system("stty echo")



