import tkinter as tk
from tkinter import scrolledtext
import requests
import json

# Function to get the token from cookies.json
def get_token_from_cookies():
    with open('cookies.json', 'r') as file:
        cookies = json.load(file)
        for cookie in cookies:
            if cookie['name'] == 'token':
                return cookie['value']
    return None

# Function to send the input text to the Hugging Face model and get the response
def get_ai_response(input_text):
    token = get_token_from_cookies()
    if token is None:
        return "Token not found in cookies.json"

    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    # Correct API URL for the model
    url = "https://api-inference.huggingface.co/models/meta-llama/Meta-Llama-3.1-70B-Instruct"
    payload = {
        "inputs": input_text  # Modify this based on model requirements
    }

    response = requests.post(url, headers=headers, json=payload)
    if response.status_code == 200:
        return response.json()  # Adjust according to the expected response
    else:
        return f"Error: {response.status_code} - {response.text}"

# Function to handle the send button click
def on_send():
    user_input = input_text.get("1.0", tk.END).strip()
    if user_input:
        chat_area.config(state=tk.NORMAL)
        chat_area.insert(tk.END, f"You: {user_input}\n")
        input_text.delete("1.0", tk.END)

        response = get_ai_response(user_input)
        chat_area.insert(tk.END, f"AI: {response}\n")
        chat_area.config(state=tk.DISABLED)

# Create the main application window
app = tk.Tk()
app.title("Chat with AI")

# Create a chat area
chat_area = scrolledtext.ScrolledText(app, wrap=tk.WORD, state=tk.DISABLED, width=50, height=20)
chat_area.pack(pady=10)

# Create an input area
input_text = tk.Text(app, height=3)
input_text.pack(pady=10)

# Create a send button
send_button = tk.Button(app, text="Send", command=on_send)
send_button.pack(pady=10)

# Start the application
app.mainloop()
