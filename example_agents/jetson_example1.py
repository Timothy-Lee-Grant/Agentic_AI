import ollama

def StatusOfLightsInRoom():
    return "All lights are currently on."

def TemperatureInRoom():
    return "20 degrees Celcius."

StatusOfLightsInRoomPtr = StatusOfLightsInRoom()
TemperatureInRoomPtr = TemperatureInRoom()

messages = [
    {
        "role": "system",
        "content": """You are an AI assistant that can request tools when needed"
            AVAILABLE TOOLS:
            - StatusOfLightsInRoom : Returns the state of all the lights in the user's room.
                Format: {"tool": "StatusOfLightsInRoom", "args": ""}
            - TemperatureInRoom : Returns the temperature inside the user's room.
                Format: {"tool": "TemperatureInRoom", "args": ""}

            RULES:
            1. You may only request tools which are provided in the AVAILABLE TOOLS list
            2. If no tool is needed answer normally.
            """
    },
    {
        "role": "user",
        "content": ""
    }
]

while True:
    userInput = input(">>>")
    if userInput == 'q' or userInput == 'quit':
        exit()
    messages[1]["content"] = userInput
    response = ollama.chat(model = 'llama3:8b', messages=messages)
    if response['message']['content'] == '{"tool": "StatusOfLightsInRoom", "args": ""}':
        messages.append({"role":"tool", "content": {StatusOfLightsInRoomPtr}})
        response = ollama.chat(model='llama3:8b', messages=messages)
        print(response['message']['content'])
    elif response['message']['content'] == '{"tool": "TemperatureInRoom", "args": ""}':
        messages.append({"role":"tool", "content": {TemperatureInRoomPtr}})
        response = ollama.chat(model='llama3:8b', messages=messages)
        print(response['message']['content'])
    else:
        print(response['message']['content'])