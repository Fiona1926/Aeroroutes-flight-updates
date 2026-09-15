from langchain_huggingface import HuggingFaceEndpointEmbeddings, HuggingFaceEndpoint, ChatHuggingFace
from langchain_ollama import ChatOllama
from langchain_text_splitters import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import TextLoader #why is there no thiss one
from langchain_core.documents import Document
from langchain_core.prompts import ChatPromptTemplate
from langchain_chroma import Chroma
from langchain_classic.chains import create_retrieval_chain
from langchain_classic.chains.combine_documents import create_stuff_documents_chain
import chromadb
from dotenv import load_dotenv
import os

load_dotenv()
HF_TOKEN = os.environ.get("HF_API_TOKEN")

# 1. load the text file
def load_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        text = file.read()
    return [Document(page_content=text, metadata={"source": file_path})]  #list

docs = load_text_file('/Users/fionaleong/aeroroutes_flight_monitor/data/rss_all.txt')

# 2. recursive characther chunking : set up splitter and split the documents
text_splitter = RecursiveCharacterTextSplitter(chunk_size=1000, chunk_overlap=100)
splits = text_splitter.split_documents(docs)
print(f"Split into {len(splits)} chunks.")

# 2. set up embeddings 
embeddings_model = HuggingFaceEndpointEmbeddings(
    model="sentence-transformers/all-mpnet-base-v2",
    task="feature-extraction", 
    huggingfacehub_api_token=HF_TOKEN,
)

# 3. set up chromadb and store document in vector store
client= chromadb.PersistentClient(path='./chroma_db')
try:
    client.delete_collection("file_embeddings")
    print("Deleted existing collection 'file_embeddings'.")
except Exception:
    print("No existing collection to delete.")


vector_store = Chroma.from_documents(
    documents= splits,
    collection_name='file_embeddings',
    embedding=embeddings_model,        #set up the vector store and what embedding model that is used for this vector store
    persist_directory='./chroma_db',
)

print(f"Added {len(splits)} chunks to Chroma.")

# 4. doing semantic search to obtain the results

retriever=vector_store.as_retriever(
    search_type="similarity",       # or "mmr", "similarity_score_threshold"
    search_kwargs={"k": 5}          # return top 5 results
)

query='Is there any increase in the frequency of flights?'
ans= retriever.invoke(query) #test out the answer

# 5. set up llm chat model
'''
llm = HuggingFaceEndpoint(
    repo_id="Qwen/Qwen3.5-27B",
    huggingfacehub_api_token=HF_TOKEN,
    provider="novita",  
    task="text-generation",
)
chat = ChatHuggingFace(llm=llm)

'''
chat= ChatOllama(
    model="llama3",     #latest llama multimodal, but this is very innaccurate. temp=0.3 is very much not context aware. 
    temperature=0.5
)


chat_template= ChatPromptTemplate.from_messages([
    ("system",
     "You are a helpful aviation assistant, telling inbformation about flights. Answer the question using ONLY the context below. "
     "If the answer is not in the context, say 'There is no information in aeroroutes reagarding your questions'.\n\n"
     "Context:\n{context}"),
    ("human", "{input}")
])

#from_documents and add_documents: from is creating the chromq and adding them

#retrieval chain
qa_chain = create_stuff_documents_chain(chat, chat_template) #replaces LCEl, manual chain making, will take list of docs and stuff into prompt and get the llm
#retrieval plus generation
rag_chain = create_retrieval_chain(retriever, qa_chain) #calls retriever.invoke()
