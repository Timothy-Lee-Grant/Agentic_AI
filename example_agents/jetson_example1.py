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


