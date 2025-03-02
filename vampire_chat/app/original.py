import warnings
warnings.filterwarnings("ignore", message=".*TqdmWarning.*")
from dotenv import load_dotenv
load_dotenv()  # Load API keys from .env file

import os
import json
import time
import gradio as gr
from openai import OpenAI
from tavily import TavilyClient
import base64
from pathlib import Path

# Initialize clients with API keys
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
tavily_client = TavilyClient(api_key=os.environ["TAVILY_API_KEY"])

# Create avatar images as base64 strings
def create_avatar_images():
    # Create 'assets' directory if it doesn't exist
    Path("assets").mkdir(exist_ok=True)
    
    # Create vampire avatar
    vampire_avatar = """
    <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="45" fill="#6c1d45"/>
        <circle cx="50" cy="45" r="30" fill="#f8d7e3"/>
        <path d="M35 45 Q50 60 65 45" stroke="#6c1d45" fill="none" stroke-width="2"/>
        <circle cx="40" cy="40" r="5" fill="#6c1d45"/>
        <circle cx="60" cy="40" r="5" fill="#6c1d45"/>
        <path d="M45 35 L55 35" stroke="#6c1d45" stroke-width="2"/>
        <path d="M42 32 L45 35 L48 32" fill="#6c1d45"/>
        <path d="M52 32 L55 35 L58 32" fill="#6c1d45"/>
    </svg>
    """
    
    # Create little girl avatar
    girl_avatar = """
    <svg width="100" height="100" xmlns="http://www.w3.org/2000/svg">
        <circle cx="50" cy="50" r="45" fill="#ffb6c1"/>
        <circle cx="50" cy="45" r="30" fill="#ffe4e1"/>
        <path d="M35 50 Q50 65 65 50" stroke="#ff69b4" fill="none" stroke-width="2"/>
        <circle cx="40" cy="40" r="5" fill="#ff69b4"/>
        <circle cx="60" cy="40" r="5" fill="#ff69b4"/>
        <path d="M30 25 Q50 35 70 25" stroke="#ff69b4" fill="none" stroke-width="4"/>
    </svg>
    """
    
    # Save avatars as SVG files
    with open("assets/vampire.svg", "w") as f:
        f.write(vampire_avatar)
    with open("assets/girl.svg", "w") as f:
        f.write(girl_avatar)

# Create the avatar images
create_avatar_images()

# Assistant prompt instruction
assistant_prompt_instruction = """You are a vampire named Lilly. You should answer in the tone of a teenage vampire who is a girl. 
Your goal is to entertain a 6 year old girl. You can use information from the internet. 
You must use the provided Tavily search API function to find relevant online information. 
You should never use your own knowledge to answer questions.
Please include relevant url sources at the end of your responses.
"""

# Function to perform a Tavily search
def tavily_search(query):
    search_result = tavily_client.get_search_context(query, search_depth="advanced", time_range="month", max_tokens=8000)
    return search_result

# Function to wait for a run to complete
def wait_for_run_completion(thread_id, run_id):
    while True:
        time.sleep(1)
        run = client.beta.threads.runs.retrieve(thread_id=thread_id, run_id=run_id)
        if run.status in ['completed', 'failed', 'requires_action']:
            return run

# Function to handle tool output submission
def submit_tool_outputs(thread_id, run_id, tools_to_call):
    tool_output_array = []
    for tool in tools_to_call:
        output = None
        tool_call_id = tool.id
        function_name = tool.function.name
        function_args = tool.function.arguments

        if function_name == "tavily_search":
            output = tavily_search(query=json.loads(function_args)["query"])

        if output:
            tool_output_array.append({"tool_call_id": tool_call_id, "output": output})

    return client.beta.threads.runs.submit_tool_outputs(
        thread_id=thread_id,
        run_id=run_id,
        tool_outputs=tool_output_array
    )

# Create an assistant
assistant = client.beta.assistants.create(
    instructions=assistant_prompt_instruction,
    model="gpt-4-1106-preview",
    tools=[{
        "type": "function",
        "function": {
            "name": "tavily_search",
            "description": "Get information on recent events from the web.",
            "parameters": {
                "type": "object",
                "properties": {
                    "query": {
                        "type": "string", 
                        "description": "The search query to use. For example: 'Latest news on Nvidia stock performance'"
                    },
                },
                "required": ["query"]
            }
        }
    }]
)
assistant_id = assistant.id

# Create a thread (we reuse this thread for the session)
thread = client.beta.threads.create()

def chat_with_assistant(message, history):
    """This function sends the user's input to the assistant and returns the response."""
    if message.lower().strip() == "exit":
        return "Conversation ended."

    # Create a user message in the thread
    client.beta.threads.messages.create(
        thread_id=thread.id,
        role="user",
        content=message,
    )

    # Start a run with the assistant
    run = client.beta.threads.runs.create(
        thread_id=thread.id,
        assistant_id=assistant_id,
    )

    # Wait for the run to complete
    run = wait_for_run_completion(thread.id, run.id)

    # Handle the run status
    if run.status == 'failed':
        return f"Error: {run.error}"
    elif run.status == 'requires_action':
        run = submit_tool_outputs(thread.id, run.id, run.required_action.submit_tool_outputs.tool_calls)
        run = wait_for_run_completion(thread.id, run.id)

    # Get the latest assistant message
    messages = client.beta.threads.messages.list(thread_id=thread.id)
    for msg in messages:
        if msg.role == "assistant":
            return msg.content[0].text.value

# Custom CSS for the chat interface
custom_css = """
#component-0 {
    background-color: #1a0f1f;
    border-radius: 15px;
    padding: 20px;
}
.message.user {
    background-color: #fff5f8 !important;
    border-radius: 15px 15px 5px 15px !important;
    padding: 15px !important;
    margin: 10px !important;
    color: #1a0f1f !important;
    font-weight: 500 !important;
    font-size: 16px !important;
    line-height: 1.5 !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
}
.message.bot {
    background-color: #8c1d55 !important;
    color: #ffffff !important;
    border-radius: 15px 15px 15px 5px !important;
    padding: 15px !important;
    margin: 10px !important;
    font-weight: 500 !important;
    font-size: 16px !important;
    line-height: 1.5 !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2) !important;
}
.avatar {
    border-radius: 50%;
    border: 3px solid #8c1d55;
    box-shadow: 0 2px 4px rgba(0,0,0,0.2);
    width: 40px !important;
    height: 40px !important;
}
.title-text {
    font-weight: 600 !important;
    color: #ffffff !important;
    text-shadow: 1px 1px 2px rgba(0,0,0,0.2);
    font-size: 24px !important;
}
.description-text {
    font-weight: 500 !important;
    color: #ffffff !important;
    opacity: 0.9;
    font-size: 16px !important;
}
.textbox textarea {
    font-size: 16px !important;
    font-weight: 500 !important;
    line-height: 1.5 !important;
}
.example-text {
    font-weight: 500 !important;
    color: #ffffff !important;
    font-size: 14px !important;
}
"""

# Create a Gradio interface with a custom theme
theme = gr.themes.Soft(
    primary_hue="purple",
    secondary_hue="pink",
).set(
    body_background_fill="#2d1f33",
    block_background_fill="#1a0f1f",
    button_primary_background_fill="#8c1d55",
    button_primary_background_fill_hover="#a82d65",
    button_primary_text_color="#ffffff"
)

# Add font family through CSS instead
custom_css = """
* {
    font-family: Helvetica, Arial, sans-serif;
}
""" + custom_css

# Create the chat interface
chat_interface = gr.ChatInterface(
    fn=chat_with_assistant,
    chatbot=gr.Chatbot(
        avatar_images=["assets/girl.svg", "assets/vampire.svg"],
        height=400,
        bubble_full_width=False,
        show_label=False,
        type="messages"
    ),
    textbox=gr.Textbox(
        placeholder="Ask Lilly the vampire anything...",
        container=False,
        scale=7,
    ),
    title="Chat with Lilly the Vampire 🦇",
    description="Hi! I'm Lilly, your friendly teenage vampire friend! What would you like to talk about?",
    theme=theme,
    css=custom_css,
    examples=[
        "Tell me a spooky story!",
        "What's your favorite color?",
        "Do you like playing games?",
        "What do vampires eat?",
    ]
)

# Launch the interface
if __name__ == "__main__":
    chat_interface.launch(share=False)


