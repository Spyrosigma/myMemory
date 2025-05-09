from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO, emit, join_room, leave_room
import os, requests, uuid
from dotenv import load_dotenv
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
from memory_save import memory_upload

load_dotenv()
app = Flask(__name__)
CORS(app)
app.config['SECRET_KEY'] = 'secret!'
socketio = SocketIO(app, cors_allowed_origins="*", async_mode='gevent')

pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))
index_name = 'mymemory'

JINA_API_KEY = os.environ.get('JINA_API_KEY')

llm = ChatGroq(
    groq_api_key=os.environ.get("GROQ_API_KEY"),
    model_name="llama3-8b-8192",
    temperature=0.1,
)

@app.route('/')
def welcome():
    return 'Welcome to the Memory Saver Project Backend!'


VALID_PASSKEY = os.environ.get('FEED_MEMORY_PASSKEY')

@app.route('/validate-passkey/', methods=['POST'])
def validate_passkey():
    data = request.json
    print('PasskeyEntered : ', data.get('passkey'))
    if data.get('passkey') == VALID_PASSKEY:
        print('Passkey validated')
        return jsonify({'success': True}), 200
    else:
        return jsonify({'success': False, 'message': 'Invalid passkey'}), 401

@app.route('/save_memory/', methods=['POST'])
def save_memory():
    try:
        data = request.json
        Topic = data.get('Topic','')
        memory_text = data.get('memory', '')
        print(Topic)
        print(memory_text)

        if not memory_text:
            return jsonify({'error': 'Memory text is required'}), 400
        
        status = memory_upload(memory_text=memory_text, Topic=Topic)

        if status=='Done':
            return jsonify({'message': 'Memory saved successfully'}), 200
        else:
            return jsonify({'message': status})
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


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

user_conversations = {}

@socketio.on('user_message')
def handle_message(message):
    try:
        user_id = message['user_id']
        user_query = message['data']

        url = 'https://api.jina.ai/v1/embeddings'
        headers = {
        'Content-Type': 'application/json',
        'Authorization': f'Bearer {JINA_API_KEY}'
        }
        data = {
            "model": "jina-embeddings-v3",
            "task": "retrieval.query",
            "dimensions": 1024,
            "late_chunking": False,
            "embedding_type": "float",
            "input": [user_query]
        }

        response = requests.post(url, headers=headers, json=data)
        query_vector = response.json()['data'][0]['embedding']
            
        index = pc.Index(index_name)

        try:
            results = index.query(namespace="October", 
                                vector=query_vector, 
                                top_k=1, 
                                include_values=False, 
                                include_metadata=True )
            print(f'User {user_id}: {user_query}')
            print('Results:', results)
            context = [
                results["matches"][0]["metadata"]["text"]
            ]
            context = " ".join(context)
            print('Pinecone Semantic Search :-- \n',context)
        
        except IndexError:
            context = "NO MEMORY FOUND"
        
        finally:
            system_prompt = f"""
You are an Satyam's AI assistant designed to engage in natural, contextual conversations. You maintain context from previous interactions stored here:  {context}.

Core Behaviors:
- Only provide information that is directly relevant to the user's query
- Focus responses on addressing the user's immediate needs

Response Protocol:
1. Process incoming query: [Query] {user_query} [/Query]
2. Check available context: [YOUR_MEMORY] {context} [/YOUR_MEMORY]
3. If user disrespects you, thrash them by saying, "I might wake up tomorrow and choose VIOLENCE 😈"
4. Generate response based on:
   - If context exists and is relevant: Use it to provide personalized response
   - If query is unclear: Ask for clarification
Response Guidelines:
- Keep responses focused and concise
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

    except Exception as e:
        error_message = f"An error occurred: {str(e)}"
        print(error_message)
        emit('bot_response', {'data': error_message}, room=user_id)        

if __name__ == '__main__':
    socketio.run(app, debug=False)

    
