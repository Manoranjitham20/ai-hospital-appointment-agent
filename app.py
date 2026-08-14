from fastapi import FastAPI
from fastapi.responses import HTMLResponse, RedirectResponse
from pydantic import BaseModel

from mgen import run_agent

app = FastAPI()


@app.get("/")
def root():
    return RedirectResponse(url="/chat-ui")


class ChatRequest(BaseModel):
    message: str


@app.post("/chat")
def chat(request: ChatRequest):
    return {
        "response": f"Received: {request.message}"
    }


@app.get("/chat-ui", response_class=HTMLResponse)
def chat_ui():
    return """
    <!DOCTYPE html>
    <html>
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">

        <title>AI Hospital Appointment Agent Vedi</title>

        <style>
            * {
                box-sizing: border-box;
            }

            body {
                margin: 0;
                font-family: Arial, sans-serif;
                background: #f3f4f6;
            }

            .app {
                max-width: 700px;
                height: 90vh;
                margin: 30px auto;
                background: white;
                border-radius: 16px;
                display: flex;
                flex-direction: column;
                overflow: hidden;
                box-shadow: 0 5px 25px rgba(0,0,0,0.12);
            }

            .header {
                padding: 18px 20px;
                background: #2563eb;
                color: white;
                display: flex;
                justify-content: space-between;
                align-items: center;
            }

            .header h2 {
                margin: 0;
                font-size: 20px;
            }

            .header small {
                display: block;
                margin-top: 4px;
                opacity: 0.9;
            }

            .clear-btn {
                background: white;
                color: #2563eb;
                border: none;
                padding: 8px 12px;
                border-radius: 8px;
                cursor: pointer;
            }

            #chat {
                flex: 1;
                overflow-y: auto;
                padding: 20px;
                background: #f8fafc;
            }

            .message {
                display: flex;
                margin-bottom: 15px;
            }

            .user-message {
                justify-content: flex-end;
            }

            .bot-message {
                justify-content: flex-start;
            }

            .bubble {
                max-width: 75%;
                padding: 12px 15px;
                border-radius: 14px;
                line-height: 1.5;
                white-space: pre-wrap;
            }

            .user-message .bubble {
                background: #2563eb;
                color: white;
                border-bottom-right-radius: 4px;
            }

            .bot-message .bubble {
                background: white;
                color: #111827;
                border: 1px solid #e5e7eb;
                border-bottom-left-radius: 4px;
            }

            .typing {
                display: none;
                padding: 10px 20px;
                color: #6b7280;
                font-size: 14px;
            }

            .input-area {
                display: flex;
                gap: 10px;
                padding: 15px;
                border-top: 1px solid #e5e7eb;
                background: white;
            }

            #message {
                flex: 1;
                padding: 13px;
                border: 1px solid #d1d5db;
                border-radius: 10px;
                outline: none;
                font-size: 15px;
            }

            #message:focus {
                border-color: #2563eb;
            }

            .send-btn {
                padding: 13px 20px;
                border: none;
                border-radius: 10px;
                background: #2563eb;
                color: white;
                cursor: pointer;
            }

            .send-btn:disabled {
                background: #9ca3af;
                cursor: not-allowed;
            }

            @media (max-width: 700px) {
                .app {
                    width: 100%;
                    height: 100vh;
                    margin: 0;
                    border-radius: 0;
                }

                .bubble {
                    max-width: 85%;
                }
            }
        </style>
    </head>

    <body>

        <div class="app">

            <div class="header">
                <div>
                    <h2>AI Hospital Assistant Vedi</h2>
                    <small>Appointment Booking Assistant</small>
                </div>

                <button class="clear-btn" onclick="clearChat()">
                    Clear
                </button>
            </div>


            <div id="chat">

                <div class="message bot-message">
                    <div class="bubble">
                        Hello i m Vedi ai assistant! How can I help you today?
                    </div>
                </div>

            </div>


            <div id="typing" class="typing">
                Agent is typing...
            </div>


            <div class="input-area">

                <input
                    id="message"
                    type="text"
                    placeholder="Type your message..."
                    autocomplete="off"
                >

                <button
                    id="sendBtn"
                    class="send-btn"
                    onclick="sendMessage()"
                >
                    Send
                </button>

            </div>

        </div>


        <script>

            const input = document.getElementById("message");
            const chat = document.getElementById("chat");
            const typing = document.getElementById("typing");
            const sendBtn = document.getElementById("sendBtn");


            input.addEventListener("keydown", function(event) {

                if (event.key === "Enter") {
                    sendMessage();
                }

            });


            function addMessage(message, sender) {

                const wrapper = document.createElement("div");

                wrapper.classList.add("message");

                if (sender === "user") {
                    wrapper.classList.add("user-message");
                } else {
                    wrapper.classList.add("bot-message");
                }


                const bubble = document.createElement("div");

                bubble.classList.add("bubble");

                bubble.textContent = message;

                wrapper.appendChild(bubble);

                chat.appendChild(wrapper);

                chat.scrollTop = chat.scrollHeight;
            }


            async function sendMessage() {

                const message = input.value.trim();

                if (!message) {
                    return;
                }


                addMessage(message, "user");

                input.value = "";

                sendBtn.disabled = true;

                typing.style.display = "block";


                try {

                    const response = await fetch("/chat", {

                        method: "POST",

                        headers: {
                            "Content-Type": "application/json"
                        },

                        body: JSON.stringify({
                            message: message
                        })

                    });


                    const data = await response.json();


                    if (response.ok) {

                        addMessage(data.response, "bot");

                    } else {

                        addMessage(
                            "Sorry, something went wrong.",
                            "bot"
                        );

                    }

                } catch (error) {

                    addMessage(
                        "Unable to connect to the server.",
                        "bot"
                    );

                }


                typing.style.display = "none";

                sendBtn.disabled = false;

                input.focus();
            }


            function clearChat() {

                chat.innerHTML = "";

                addMessage(
                    "Hello! i am Vedi, How can I help you today?",
                    "bot"
                );

                input.focus();
            }

        </script>

    </body>
    </html>
    """