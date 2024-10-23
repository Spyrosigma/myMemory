from flask import Flask
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import os
from dotenv import load_dotenv
import uuid
from pinecone import Pinecone
from langchain.chains import ConversationChain
from langchain.memory import ConversationBufferMemory
from langchain_core.prompts import (
    ChatPromptTemplate,
    HumanMessagePromptTemplate,
    MessagesPlaceholder,
)
from langchain_core.messages import SystemMessage
from langchain_groq import ChatGroq

load_dotenv()
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

llm = ChatGroq(
    groq_api_key=os.environ.get("GROQ_API_KEY"),
    model_name="llama3-8b-8192",
    temperature=0.1,
)
user_conversations = {}

@socketio.on('connect')
def handle_connect():
    user_id = str(uuid.uuid4())
    join_room(user_id)
    emit('set_user_id', {'user_id': user_id})
    print(f'Client connected with ID: {user_id}')

@socketio.on('join')
def on_join(data):
    user_id = data['user_id']
    join_room(user_id)
    print(f'User {user_id} joined their room')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))
index_name = 'mymemory'


@socketio.on('user_message')
def handle_message(message):
    user_id = message['user_id']
    user_query = message['data']
    
    query = user_query

    query = pc.inference.embed(
        "multilingual-e5-large",
        inputs=[query],
        parameters={
            "input_type": "query"
        }
    )
    index = pc.Index(index_name)
    results = index.query(namespace="mymemory", 
                        vector=query[0].values, 
                        top_k=2, 
                        include_values=False, 
                        include_metadata=True )

    print(f'User {user_id}: {user_query}')
    print('---------------------------------------------------------')
    context = [
        results["matches"][0]["metadata"]["text"],
        results["matches"][1]["metadata"]["text"],
    ]
    context = " ".join(context)
    print('Pinecone Semantic Search :-- \n',context)

    
    system_prompt = f"""
    You are a expert in Indian Legal System. You are here to help the user with their queries.
    Based on the USER QUERY: {query} and the given CONTEXT : {context} , please provide a response.

    Guidlines:
    - Keep the answer short and to the point.
    - If you don't know the answer, say 'I don't know'
    - If you need more information, ask the user.
    """


    if user_id not in user_conversations:
        memory = ConversationBufferMemory(return_messages=True)
        prompt = ChatPromptTemplate.from_messages([
            SystemMessage(content=system_prompt),
            MessagesPlaceholder(variable_name="history"),
            HumanMessagePromptTemplate.from_template("{input}")
        ])
        user_conversations[user_id] = ConversationChain(
            llm=llm,
            memory=memory,
            prompt=prompt,
            verbose=False
        )

    conversation = user_conversations[user_id]
    response = conversation.predict(input=user_query)
    
    print('Groq: ', response)
    emit('bot_response', {'data': response}, room=user_id)

if __name__ == '__main__':
    socketio.run(app, debug=True)

    
