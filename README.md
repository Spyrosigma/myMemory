# MyMemory - Your Personal AI Memory Assistant

MyMemory is a full-stack application designed to help you store, manage, and recall your memories using a conversational AI interface. It allows you to feed your memories into a secure system and then chat with an AI assistant that can retrieve and discuss these memories with context.

[![Portfolio](https://img.shields.io/badge/Author-SpyroSigma-blue?style=flat-square&logo=github)](https://spyrosigma.vercel.app)

## Features

* **Save Memories:** Securely store your memories with a topic and detailed content.
* **AI Chat Interface:** Converse with an AI assistant (powered by Llama3 via Groq) to recall and discuss your stored memories.
* **Semantic Search:** Memories are retrieved based on semantic similarity to your queries, providing relevant results.
* **Real-time Interaction:** Uses Socket.IO for a responsive chat experience.
* **Speech-to-Text:** Input chat messages using your voice.
* **Passkey Protection:** The memory feeding section is protected by a passkey.
* **Personalized Experience:** Conversations are contextual and user-specific.

## Tech Stack

**Backend:**

* **Framework:** Flask (Python)
* **Real-time Communication:** Flask-SocketIO
* **Vector Database:** Pinecone
* **Embeddings:** Jina AI (jina-embeddings-v3)
* **LLM Integration:** Langchain, ChatGroq (llama3-8b-8192)
* **Deployment:** (Assumed, e.g., Koyeb as hinted in frontend `.env`)

**Frontend:**

* **Framework:** Next.js (React)
* **Language:** TypeScript
* **Styling:** Tailwind CSS
* **UI Components:** Shadcn UI
* **Real-time Communication:** Socket.IO Client
* **Deployment:** Vercel (implied by Vercel Analytics)


## Setup and Installation

### Prerequisites

* Node.js (v18 or later recommended)
* Python (v3.8 or later recommended)
* `pip` (Python package installer)
* Access to Pinecone, Jina AI, and Groq API keys.

### Backend Setup

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/your-username/spyrosigma-mymemory.git](https://github.com/your-username/spyrosigma-mymemory.git)
    cd spyrosigma-mymemory/backend
    ```

2.  **Create a virtual environment (recommended):**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows: venv\Scripts\activate
    ```

3.  **Install dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

4.  **Set up environment variables:**
    Create a `.env` file in the `backend` directory and add the following:
    ```env
    PINECONE_API_KEY="YOUR_PINECONE_API_KEY"
    JINA_API_KEY="YOUR_JINA_AI_API_KEY"
    GROQ_API_KEY="YOUR_GROQ_API_KEY"
    FEED_MEMORY_PASSKEY="YOUR_CHOSEN_PASSKEY_FOR_FEEDING_MEMORIES"
    SECRET_KEY="YOUR_FLASK_SECRET_KEY" # For Flask session management, e.g., generate with os.urandom(24).hex()
    ```
    * `PINECONE_API_KEY`: Your API key for Pinecone.
    * `JINA_API_KEY`: Your API key for Jina AI (for embeddings).
    * `GROQ_API_KEY`: Your API key for Groq (for Llama3 model access).
    * `FEED_MEMORY_PASSKEY`: A secret passkey you define to protect the memory feeding functionality.
    * `SECRET_KEY`: A secret key for Flask app security.

5.  **Run the backend server:**
    For development:
    ```bash
    python app.py
    ```
    For production (using Gunicorn, as it's in `requirements.txt`):
    ```bash
    gunicorn --worker-class geventwebsocket.gunicorn.workers.GeventWebSocketWorker -w 1 app:app
    ```
    The backend will typically run on `http://127.0.0.1:5000`.

### Frontend Setup

1.  **Navigate to the frontend directory:**
    ```bash
    cd ../frontend
    ```

2.  **Install dependencies:**
    ```bash
    npm install
    # or
    # yarn install
    ```

3.  **Set up environment variables:**
    Create a `.env.local` file in the `frontend` directory (or rename/copy the existing `.env` file).
    The primary variable needed is:
    ```env
    NEXT_PUBLIC_BACKEND_URL="http://localhost:5000"
    ```
    If you have deployed your backend, replace `http://localhost:5000` with your backend's public URL (e.g., the Koyeb URL `https://petite-terra-hanumansingh-445ce1a4.koyeb.app/` found in your provided `.env`).

4.  **Run the frontend development server:**
    ```bash
    npm run dev
    # or
    # yarn dev
    ```
    The frontend will typically run on `http://localhost:3000`.

## How It Works

### Memory Saving

1.  **Input:** The user provides a "Topic" and "Memory Details" through the frontend interface after unlocking with a passkey.
2.  **API Call:** The frontend sends this data to the `/save_memory/` endpoint on the Flask backend.
3.  **Embedding:** The backend's `memory_save.py` script takes the memory text and topic, then uses the Jina AI API (`jina-embeddings-v3` model) to generate vector embeddings.
4.  **Storage:** These embeddings, along with the original text and topic as metadata, are upserted into a Pinecone vector index (`mymemory` index, `October` namespace). Each memory gets a unique ID.

### Chatting with MyMemory

1.  **Connection:** The frontend establishes a Socket.IO connection with the backend. Each user is assigned a unique session ID.
2.  **User Query:** The user types a message or uses speech-to-text. The message is sent to the backend via Socket.IO (`user_message` event).
3.  **Query Embedding:** The backend generates an embedding for the user's query using Jina AI.
4.  **Semantic Search:** This query embedding is used to search the Pinecone index for the most semantically similar memory (top_k=1). The text from the matching memory is retrieved as context.
5.  **LLM Interaction:**
    * A system prompt is constructed, including the retrieved context.
    * Langchain's `ConversationChain` with `ConversationBufferMemory` is used to maintain conversation history for the user.
    * The ChatGroq LLM (Llama3 model) generates a response based on the user's query, the retrieved context, and the conversation history.
6.  **Response:** The AI's response is sent back to the frontend via Socket.IO (`bot_response` event) and displayed in the chat interface.

## API Endpoints (Backend)

* `GET /`: Welcome message.
* `POST /validate-passkey/`: Validates the passkey for accessing the memory feeding section.
    * Request Body: `{ "passkey": "your_passkey" }`
    * Response: `{ "success": true }` or `{ "success": false, "message": "Invalid passkey" }`
* `POST /save_memory/`: Saves a new memory.
    * Request Body: `{ "Topic": "memory_topic", "memory": "memory_content" }`
    * Response: `{ "message": "Memory saved successfully" }` or error.

### Socket.IO Events (Backend)

* `connect`: Client connects, a `user_id` is generated and sent back.
* `set_user_id` (emitted by server): Sends the unique `user_id` to the client.
* `join` (emitted by client): Client joins a room based on their `user_id`.
* `disconnect`: Client disconnects.
* `user_message` (emitted by client): Client sends a chat message.
    * Payload: `{ "data": "user_query_text", "user_id": "client_user_id" }`
* `bot_response` (emitted by server): Server sends the AI's response.
    * Payload: `{ "data": "ai_response_text" }`

## Environment Variables Summary

**Backend (`backend/.env`):**

* `PINECONE_API_KEY`: Your Pinecone API key.
* `JINA_API_KEY`: Your Jina AI API key.
* `GROQ_API_KEY`: Your Groq API key.
* `FEED_MEMORY_PASSKEY`: Custom passkey for memory input.
* `SECRET_KEY`: Flask secret key.

**Frontend (`frontend/.env.local`):**

* `NEXT_PUBLIC_BACKEND_URL`: URL of the deployed or local backend (e.g., `http://localhost:5000`).

## Contributing

Contributions are welcome! If you'd like to contribute, please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/your-feature-name`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/your-feature-name`).
6.  Open a Pull Request.

Please ensure your code follows the existing style and includes tests where appropriate.

## Author

* **Satyam (SpyroSigma)**
* Portfolio: [spyrosigma.tech](https://spyrosigma.tech)
* GitHub: [github.com/spyrosigma](https://github.com/spyrosigma)

## License

Consider adding a license to your project, such as the MIT License. To do this, create a `LICENSE` file in the root of your project and add the license text.

Example for MIT License:

MIT License

Copyright (c) [2025] [SpyroSigma]

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.


