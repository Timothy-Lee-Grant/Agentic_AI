import ollama

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

'''
tool_determiner_prompt = [{
        "role": "system",
        "content": """Your task is to determine if a tool is required to answer the user's question.
        Look at the user's input and determine if one of the following tools is reqired.
        If no tool fits the user's prompt, respond "No Tool Required"
        Available Tools:
        1. Get Temperatute:
        2. Get Lighting Status"""
    },{
        "role": "user",
        "content": ""
    }]
'''

#I don't quite feel comfortable with this change in the system prompt because this is explicitly telling the LLM what keywords to look out for. This is much more similar to programmatically using keywords to branch. 
#Instead, I should be using the LLM to determine intent of the question to see if it matches a tool.
tool_determiner_prompt = [{
        "role": "system",
        "content": """Determine if the user is asking or mentioning room conditions like 
        heat, cold, lighting. If they mention being hot or cold, use the Temperature tool. 
        If they mention being dark or bright, or lights, use the Lights tool."""
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


PIPER_PATH = "/home/timothy/Desktop/Agentic_AI/sound_processing/piper/piper"
MODEL_PATH =  "/home/timothy/Desktop/Agentic_AI/sound_processing/en_US-lessac-medium.onnx"

def speak(text):
    print(f"Speaking {text}")

    command = f'echo "{text}" | {PIPER_PATH} --model {MODEL_PATH} --output_raw | aplay -r 22050 -f S16_LE -t raw -c 1 -D plughw:0,0'

    subprocess.run(command, shell=True)







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






while True:
    userInput = input(">>>")
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
    # --- SLIDING WINDOW ---
    # Keep the system prompt (index 0) + the last 10 messages
    #if len(messages) > 11:
    #    messages = [messages[0]] + messages[-10:]
    # ----------------------


