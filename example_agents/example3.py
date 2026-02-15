import ollama
import json
#import psutil

def get_ram_usage():
    #return f"Current RAM usage: {ram_usage}%"
    return "Total 100GB, Used: 10GB"

ram_info = get_ram_usage()

messages = [
    {
        'role': 'system',
        'content': """You are an agent that can request tools when needed.
        If you need system RAM information, respond ONLY with a JSON object:
        
        AVAILABLE TOOLS:
        - get_ram_usage(): returns RAM usage Information.

        RULES:
        1. You may ONLY request tools from the AVAILABLE TOOLS list.
        2. NEVER invent new tools.
        3. If you need RAM information, respond ONLY with:

        {"tool": "get_ram_usage", "arguments": {}} 

        Then after the tool is provided, answer the user's origional question.

        4. If no tool needed, answer normally."""
        
    },
    {
        'role': 'user',
        'content': ""
    }
]

TOOLS = {
    "get_ram_usage": get_ram_usage
}

def LooksLikeToolCallOld(content):
    try: 
        data = json.loads(content) 
        return "tool" in data 
    except: 
        return False

def LooksLikeToolCallNotWorking(content):
    toolName, args = ParseToolCall(content)
    if toolName not in TOOLS:
        print(f"Model requested unknown tool: {toolName}")
        messages.append({
            "role", "assistant",
            #"content": f"Error: Unknown tool '{toolName}'. Available tools: {list(TOOLS.keys())}"
        })

#Returns True if content is llm asking for tool
def LooksLikeToolCall(content):
    try:
        data = json.loads(content)
        return isinstance(data, dict) and "tool" in data
    except json.JSONDecodeError:
        return False

def ParseToolCall(content):
    try:
        data = json.loads(content)
        if "tool" in data:
            return data["tool"], data.get("arguments", {})
    except:
        return None
    return None

def RunTool(toolName, args):
    return TOOLS[toolName](**args)


response = ""
def main():
    while True:

        userInput = input("User Prompt: ")
        if userInput == 'q' or userInput == 'quit':
            return
        messages.append({"role": "user", "content": userInput})
        response = ollama.chat(model='qwen2.5:1.5b', messages=messages)
        print(f"Debugging response: {response}")
        print("")
        content = response['message']['content']
        if LooksLikeToolCall(content):
            toolName, args = ParseToolCall(content)
            result = RunTool(toolName, args)
            print(f"RunTool Result: {result}")
            print("")
            messages.append({
                "role": "tool", 
                "content": result
            })
            followup = response = ollama.chat(model='qwen2.5:1.5b', messages=messages)
            print(followup['message']['content'])
        else:
            print(content)




if __name__ == "__main__":
    main()