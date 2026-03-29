Jetson Voice Agent: Dual-Prompt Agentic Orchestration
A professional-grade, voice-activated AI companion designed to run locally on the NVIDIA Jetson Nano. This project implements a sophisticated "Dual-Prompt" architecture to solve common LLM tool-calling hallucination issues, enabling reliable home automation control and multilingual conversation through a seamless Speech-to-Text (STT) and Text-to-Speech (TTS) pipeline.

## Features
Dual-Prompt Intent Classification: Uses a dedicated "Tool Selector" system prompt to eliminate tool-use hallucinations and ensure strict adherence to available functions.

Voice-First Interface: Hands-free interaction using a speaker-microphone setup.

Multilingual Support: Automatic language detection for English and Mandarin Chinese, with localized voice synthesis.

Local Inference: All processing (LLM, STT, TTS) happens on-device for maximum privacy and low latency.

Knowledge Base Injection: Dynamically appends real-time sensor/device data into the chat context.

Contextual Memory: Maintains a rolling conversation history for natural, "chatty" interactions.

## System Architecture
The system operates via a continuous orchestration loop:

Capture: PyAudio records high-fidelity audio via a USB interface.

Transcription: Whisper.cpp (neural network) converts audio to text.

Phase 1 - Intent Selection: A strict system prompt determines if a tool (e.g., Temperature, Lights) is required.

Tool Execution: If required, Python functions fetch real-world data and wrap it in a [KNOWLEDGE BASE] tag.

Phase 2 - Response Generation: A friendly "Companion" prompt processes the user input + retrieved data to form a natural response.

Synthesis: Piper TTS generates audio in the detected language.

Playback: aplay outputs the response through the speaker.

## Hardware Requirements
Compute: NVIDIA Jetson Nano (4GB/Developer Kit recommended).

Audio: USB Speaker-Microphone Combo (tested with P10S/Generic USB Audio).

Storage: High-speed microSD card (64GB+) or external SSD.

## Software Prerequisites
Ensure the following tools are installed and paths are correctly mapped in the script:

Ollama: For running Qwen2.5 or Mistral locally.

Whisper.cpp: For high-performance C++ based transcription.

Piper TTS: For fast, local neural text-to-speech.

FFmpeg: For audio resampling.

Python Libraries:

Bash
pip install ollama pyaudio sshkeyboard
## Configuration
Update the following absolute paths in the script to match your local environment:

Python
PIPER_PATH = "/path/to/piper"
MODEL_PATH_PIPER = "/path/to/voice_model.onnx"
WHISPER_PATH = "/path/to/whisper-cli"
MODEL_PATH = "/path/to/ggml-base.bin"
Models Used
LLM: qwen2.5:7b (default) or mistral:v0.3.

STT: Whisper base.bin.

TTS: * English: en_US-lessac-medium.onnx

Mandarin: zh_CN-huayan-medium.onnx

## Usage
Start the Agent:

Bash
python3 main.py
Interaction:

Press [SPACE] to start recording your voice.

Press [ENTER] to stop recording and trigger the LLM processing.

Press [Q] to safely exit the application.

Voice Commands:

"How hot is it in here?" (Triggers TemperatureInRoom)

"Are the lights on?" (Triggers StatusOfLightsInRoom)

"你好，今天怎么样？" (Triggers Mandarin response)

## Technical Deep Dive: The Dual-Prompt Solution
To overcome the limitations of single-prompt tool calling (hallucinating tools, incorrect invocation, or over-reliance on tools), this project splits the logic:

1. The Gatekeeper (Intent Classifier)
This prompt is stripped of personality. It only knows how to classify intent. It prevents the model from "making up" tools because its sole mission is to output a tool call or nothing at all.

2. The Companion (Personality Layer)
This prompt never sees the raw tool definitions. It only sees the results of the tool calls injected as context. This ensures the model remains friendly and conversational without being bogged down by the technical syntax of function calling.

## Future Roadmap
[ ] Sliding Window Memory: Implement a token-count based history trimmer to prevent context overflow.

[ ] Home Assistant Integration: Replace mock functions with actual IoT API calls.

[ ] Wake Word Detection: Implement "Hey Jetson" functionality using Porcupine or Snowboy to remove the need for keyboard triggers.