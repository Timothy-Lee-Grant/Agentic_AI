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
#messages = [{"role": "system", "content": "You are a intelligent chatbot. You also have access to tool if you find them nessissary during conversations."}]
'''
messages = [{"role":"system", "content": """You are a home assistant.
             1. Only use the tools provided to you.
             2. If a user asks for something you cannot do with your tools, explain that you cannot do it.
             3. Never invent new tools or output JSON manually."""}]
'''
messages_old = [{'role': 'system', 'content': """You are a helpful, friendly AI companion.
             1. Talk to the user naturally.
             2. You have access to tools for lights and temperature. Only use them if the user specifically asks about the room environment.
             3. If you use a tool, do not output the JSON yourself. Just let the tool run.
             4. If you don't have a tool for a request, just answer normally as a AI companion."""}]

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

messages = [{"role": "system",
             "content": "You are a friendly AI campainion. Talk with the user in a happy and helpful way."}]

while True:
    userInput = input(">>>")
    if userInput.lower() in ['q', 'quit']: break

    #use LLM to determine if tool is required/helpful
    tool_determiner_prompt[1]["content"] = userInput
    tool_use_llm_response = ollama.chat(model='llama3.2', messages=tool_determiner_prompt, tools=available_function_ptr, keep_alive=-1)
    
    if tool_use_llm_response.message.tool_calls:
        for tool in tool_use_llm_response.message.tool_calls:
            print(f"---- Thinking: I need to use {tool.function.name} ----")
            functionToCall = available_functions[tool.function.name]
            toolOutput = functionToCall()
            #possibly we need to adjust this because it might pollute the clean 'message' history with the idea of tools. I want that messge history to not even know tools exist!!!
            messages.append({"role":"tool","content":toolOutput, "name":tool.function.name}) #do I really need to put that name field and so much information about tool in this clean history??
    #get response of llm with messages that has no history of any tool knowledge
    response = ollama.chat(model='llama3.2', messages=messages) #I don't need tools field and I also think keep_alive will continue to be set such that the model remains in ram indefinately from my last ollama call

    messages.append(response)
    print(response.message.content)


'''
    response = ollama.chat(model='llama3.2', messages=messages, tools=available_function_ptr, keep_alive=-1)
    messages.append(response.message)
    if response.message.tool_calls:
        for tool in response.message.tool_calls:
            print(f"---- Thinking: I need to use {tool.function.name} ----")
            functionToCall = available_functions[tool.function.name]
            toolOutput = functionToCall()

            messages.append({"role": "tool", "content": toolOutput, "name":tool.function.name})

        response = ollama.chat(model='llama3.2', messages=messages)
        print(response.message.content)
        #messages.append({"role": "assistant", "content": response.message.content})
        messages.append(response.message)
    else:
        print(response.message.content)

'''
