import os
import gradio as gr
from pathlib import Path
from openai import OpenAI
from dotenv import load_dotenv
import speech_recognition as sr
import numpy as np
from vampire_chat.utils.chat_history import ChatHistoryManager

# Load environment variables
load_dotenv()

# Initialize OpenAI client and chat history manager
client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
chat_manager = ChatHistoryManager()

# Initialize speech recognizer
recognizer = sr.Recognizer()

# Get the package root directory
PACKAGE_ROOT = Path(__file__).parent.parent.parent

def create_avatar_images():
    """Create and save avatar images."""
    assets_dir = PACKAGE_ROOT / "assets"
    assets_dir.mkdir(exist_ok=True)
    
    # Vampire avatar SVG
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
    
    # Little girl avatar SVG
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
    
    # Save avatars
    with open(assets_dir / "vampire.svg", "w") as f:
        f.write(vampire_avatar)
    with open(assets_dir / "girl.svg", "w") as f:
        f.write(girl_avatar)

def transcribe_audio(audio):
    """Convert audio input to text using Google Speech Recognition."""
    if audio is None:
        return None
    
    try:
        # Get the audio data and sample rate
        y = audio[1]
        sr_audio = audio[0]
        
        # Convert numpy array to audio data
        audio_data = sr.AudioData(y.tobytes(), sr_audio, 2)
        
        # Perform the transcription
        text = recognizer.recognize_google(audio_data, language="en-US")
        print(f"Transcribed text: {text}")
        return text
        
    except sr.UnknownValueError:
        print("Speech Recognition could not understand the audio")
        return None
    except sr.RequestError as e:
        print(f"Could not request results from Speech Recognition service; {e}")
        return None
    except Exception as e:
        print(f"Transcription error: {e}")
        return None

def chat_with_lilly(message, history, audio=None):
    """Handle chat interaction with the vampire assistant."""
    if audio is not None:
        # If audio is provided, transcribe it
        transcribed_text = transcribe_audio(audio)
        if not transcribed_text:
            return [{"role": "assistant", "content": "I couldn't understand the audio clearly. Could you please try speaking more clearly or use the text input instead?"}]
        # Update message with transcribed text
        message = transcribed_text
        
        # Add the transcribed message to the chat history
        history.append({"role": "user", "content": message})
    
    if message.lower().strip() == "exit":
        return [{"role": "assistant", "content": "Conversation ended."}]

    # Add user message to history if it wasn't from audio
    if audio is None:
        chat_manager.add_message(role="user", content=message)
    else:
        chat_manager.add_message(role="user", content=message)
    
    # Get relevant context from previous conversations
    context = chat_manager.get_relevant_context(message)
    
    # Format conversation for OpenAI
    messages = chat_manager.format_conversation_for_openai()
    
    # If we have relevant context, add it to the system message
    if context:
        messages[0]["content"] += f"\n\nRelevant context from previous conversations:\n{context}"
    
    # Get response from OpenAI
    response = client.chat.completions.create(
        model="gpt-4-1106-preview",
        messages=messages,
        temperature=0.7,
        max_tokens=1000
    )
    
    assistant_message = response.choices[0].message.content
    
    # Add assistant's response to history
    chat_manager.add_message(role="assistant", content=assistant_message)
    
    # Update the chat history with the new messages
    history.append({"role": "assistant", "content": assistant_message})
    
    return history

# Custom CSS for the chat interface
custom_css = """
* {
    font-family: "Crimson Text", "Goudy Old Style", Georgia, serif;
}
#component-0 {
    background-color: #E6DCF5 !important;
    border-radius: 15px;
    padding: 20px;
}
.message.user {
    background-color: #ffffff !important;
    border-radius: 15px !important;
    padding: 15px !important;
    margin: 10px !important;
    color: #000000 !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    line-height: 1.6 !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    border: 1px solid #e0e0e0 !important;
}
.message.bot {
    background-color: #ffffff !important;
    color: #000000 !important;
    border-radius: 15px !important;
    padding: 15px !important;
    margin: 10px !important;
    font-weight: 600 !important;
    font-size: 16px !important;
    line-height: 1.6 !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1) !important;
    border: 1px solid #e0e0e0 !important;
}
.avatar {
    border-radius: 50%;
    border: 2px solid #000000 !important;
    box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    width: 40px !important;
    height: 40px !important;
}
.title-text {
    font-family: "Crimson Text", "Goudy Old Style", Georgia, serif !important;
    font-weight: 700 !important;
    color: #000000 !important;
    font-size: 28px !important;
    letter-spacing: 0.03em !important;
    background-color: #ffffff !important;
    padding: 10px !important;
    border-radius: 10px !important;
}
.description-text {
    font-weight: 500 !important;
    color: #000000 !important;
    font-size: 16px !important;
    line-height: 1.6 !important;
    background-color: #ffffff !important;
    padding: 10px !important;
    border-radius: 10px !important;
    margin-top: 10px !important;
}
.textbox textarea {
    font-size: 16px !important;
    font-weight: 500 !important;
    line-height: 1.5 !important;
    background-color: #ffffff !important;
    color: #000000 !important;
    border: 1px solid #e0e0e0 !important;
}
.example-text {
    font-weight: 500 !important;
    color: #000000 !important;
    font-size: 14px !important;
    background-color: #ffffff !important;
    padding: 5px !important;
    border-radius: 5px !important;
}
"""

def create_chat_interface():
    """Create and configure the Gradio chat interface."""
    # Create avatar images
    create_avatar_images()
    
    # Start a new conversation
    chat_manager.start_new_conversation()
    
    # Create theme
    theme = gr.themes.Soft(
        primary_hue="gray",
        secondary_hue="gray",
    ).set(
        body_background_fill="#f0e6ff",
        block_background_fill="#f0e6ff",
        button_primary_background_fill="#000000",
        button_primary_background_fill_hover="#333333",
        button_primary_text_color="#ffffff"
    )
    
    # Create the chat interface with Blocks for more flexibility
    with gr.Blocks(theme=theme, css=custom_css) as chat_interface:
        with gr.Row():
            gr.HTML("<h1>Chat with Lilly the Vampire 🦇</h1>")
        
        with gr.Row():
            gr.HTML("<p>Hi! I'm Lilly, your friendly teenage vampire friend! What would you like to talk about?</p>")
        
        # Initialize chat history
        initial_history = [
            {"role": msg["role"], "content": msg["content"]}
            for msg in chat_manager.get_conversation_history()
        ]
        
        chatbot = gr.Chatbot(
            value=initial_history,
            avatar_images=[str(PACKAGE_ROOT / "assets/girl.svg"), str(PACKAGE_ROOT / "assets/vampire.svg")],
            height=600,
            bubble_full_width=False,
            show_label=False,
            type="messages",
        )
        
        with gr.Row():
            with gr.Column(scale=7):
                text_input = gr.Textbox(
                    placeholder="Type your message here...",
                    show_label=False,
                    container=False,
                )
            with gr.Column(scale=3):
                audio_input = gr.Audio(
                    sources=["microphone"],
                    type="numpy",
                    label="Or speak your message",
                    streaming=False
                )
        
        # Handle text input
        text_input.submit(
            chat_with_lilly,
            [text_input, chatbot],
            [chatbot],
        ).then(
            lambda: "",
            None,
            [text_input],
        )
        
        # Handle audio input
        audio_input.stop_recording(
            chat_with_lilly,
            [gr.State(""), chatbot, audio_input],
            [chatbot],
        ).then(
            lambda: None,  # Clear the audio input after processing
            None,
            [audio_input],
        )
        
        # Add a clear button
        with gr.Row():
            clear = gr.Button("Clear Conversation")
            clear.click(
                lambda: ([], chat_manager.start_new_conversation()),
                None,
                [chatbot],
            )
    
    return chat_interface

def main():
    """Launch the chat application."""
    chat_interface = create_chat_interface()
    chat_interface.queue().launch(
        share=False,
        show_error=True
    )

if __name__ == "__main__":
    main()
