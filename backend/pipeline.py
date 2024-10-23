from pinecone import Pinecone
import os
from langchain_pinecone import PineconeEmbeddings
from dotenv import load_dotenv 
load_dotenv()

pc = Pinecone(api_key=os.environ.get('PINECONE_API_KEY'))

index_name = "mymemory"

def embed_query(user_query):
    embeddings = PineconeEmbeddings(
        model='multilingual-e5-large',
        pinecone_api_key=os.environ.get('PINECONE_API_KEY')
    )
    query = embeddings.embed_query(user_query)
    return query
print(embed_query('T'))

# from pinecone import Pinecone, ServerlessSpec
# from langchain_pinecone import PineconeEmbeddings

# pc = Pinecone(api_key=os.environ.get("PINECONE_API_KEY"))

# from pinecone import ServerlessSpec

# cloud = os.environ.get('PINECONE_CLOUD') or 'aws'
# region = os.environ.get('PINECONE_REGION') or 'us-east-1'

# spec = ServerlessSpec(cloud=cloud, region=region)

# print(pc.describe_index(index_name).dimension)

# import aiohttp
# session = aiohttp.ClientSession()
# embeddings = PineconeEmbeddings(
#         model='multilingual-e5-large',
#         pinecone_api_key=os.environ.get('PINECONE_API_KEY')
# )

