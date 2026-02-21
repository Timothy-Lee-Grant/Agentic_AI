import ollama
#response: ChatResponse = ollama.chat(...)

def StatusOfLightsInRoom():
    """Returns the state of all the lights in the user's room."""
    return "All lights are currently on."

def TemperatureInRoom():
    """Returns the temperature inside the user's room."""
    return "20 degrees Celcius."

available_functions = {
    "StatusOfLightsInRoom": StatusOfLightsInRoom,
    "TemperatureInRoom": TemperatureInRoom
}

messages = [{"role": "system", "content":"You are a smart home assistant"}]


while True:
    userInput = input(">>>")
    if userInput.lower() in ['q', 'quit']: break

    messages.append({"role": "user", "content": userInput})


    response = ollama.chat(model='llama3.1:8b', messages=messages, tools=available_functions)
    messages.append(response.message)
    
    for tool in response.message.tool_calls or []:
        print(f"---- Thinking: I need to use {tool.function.name} ----")
        functionToCall = available_functions[tool.function.name]
        toolOutput = functionToCall()

        messages.append({"role": "tool", "content": toolOutput})

    response = ollama.chat(model='llama3.1:8b', messages=messages)
    print(response.message.content)
    messages.append({"role": "assistant", "content": response.message.content})


