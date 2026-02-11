import ollama
#import psutil

def get_ram_usage():
    #return f"Current RAM usage: {ram_usage}%"
    return "Total 100GB, Used: 10GB"

ram_info = get_ram_usage()

messages = [
    {
        'role': 'user',
        'content': f"The user's computer has the following RAM stats: {ram_info}. Explain the computer's health"
    },
    {
        'role': 'system',
        'content': "You are a literal hardware monitor. Do not calculate new numbers. Only use the numbers provided in the user prompt. Be extremely concise."
    }
]

response = ollama.chat(model='qwen2.5:0.5b', messages=messages)
print(response['message']['content'])