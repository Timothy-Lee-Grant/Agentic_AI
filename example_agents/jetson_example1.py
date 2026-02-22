import ollama
#response: ChatResponse = ollama.chat(...)

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
#messages = [{"role": "system", "content": "You are a smart home assistant. Use tools only when necessary. If you use a tool, do not talk about the JSON—just use the tool."}]
messages = [{"role": "system", "content": "You are a intelligent chatbot. You also have access to tool if you find them nessissary during conversations."}]


while True:
    userInput = input(">>>")
    if userInput.lower() in ['q', 'quit']: break

    messages.append({"role": "user", "content": userInput})


    response = ollama.chat(model='llama3.1:8b', messages=messages, tools=available_function_ptr, keep_alive=-1)
    messages.append(response.message)
    if response.message.tool_calls:
        for tool in response.message.tool_calls:
            print(f"---- Thinking: I need to use {tool.function.name} ----")
            functionToCall = available_functions[tool.function.name]
            toolOutput = functionToCall()

            messages.append({"role": "tool", "content": toolOutput, "name":tool.function.name})

        response = ollama.chat(model='llama3.1:8b', messages=messages)
        print(response.message.content)
        #messages.append({"role": "assistant", "content": response.message.content})
        messages.append(response.message)
    else:
        print(response.message.content)


