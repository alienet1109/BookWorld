import sys
sys.path.append("../")

from bw_utils import *
from modules.embedding import get_embedding_model

try:
    from langchain_experimental.generative_agents.memory import GenerativeAgentMemory
except Exception:
    from langchain_experimental.generative_agents import GenerativeAgentMemory

try:
    from langchain_classic.retrievers import TimeWeightedVectorStoreRetriever
except Exception:
    try:
        from langchain.retrievers import TimeWeightedVectorStoreRetriever
    except Exception:
        raise ImportError("装 langchain-classic")

try:
    from langchain_huggingface import HuggingFaceEmbeddings
except Exception:
    try:
        from langchain_community.embeddings import HuggingFaceEmbeddings
    except Exception:
        raise ImportError("装 langchain-huggingface/langchain_community+sentence-transformers")

try:
    from langchain_community.llms.tongyi import Tongyi
except Exception:
    try:
        from langchain_community.llms import Tongyi
    except Exception:
        Tongyi = None  

try:
    from langchain.llms import OpenAI
except Exception:
    try:
        from langchain_community.llms import OpenAI
    except Exception:
        OpenAI = None

try:
    from langchain.docstore.in_memory import InMemoryDocstore
except Exception:
    from langchain_community.docstore.in_memory import InMemoryDocstore

try:
    from langchain.vectorstores.faiss import FAISS
except Exception:
    try:
        from langchain.vectorstores import FAISS
    except Exception:
        from langchain_community.vectorstores.faiss import FAISS

# 其它基础依赖
import faiss
import math


def build_role_agent_memory(type = "ga",**kwargs):
    if type == "ga":
        llm_name = kwargs["llm_name"]
        embedding_name = kwargs["embedding_name"]
        db_name = kwargs["db_name"]
        language = kwargs["language"] if "language" in kwargs else ""
        embedding_model = get_embedding_model(embedding_name,language)
        index = faiss.IndexFlatL2(len(embedding_model.embed_query("hello world")))
        vectorstore = FAISS(
            embedding_function=embedding_model,
            index=index,
            docstore=InMemoryDocstore(),
            index_to_docstore_id={},
        )
        memory_retriever = TimeWeightedVectorStoreRetriever(vectorstore=vectorstore, other_score_keys=["importance"], k=5)
        if llm_name.startswith("qwen"):
            chat_model = Tongyi(
                temperature=0.9,
            )
        else:
            chat_model = OpenAI(
                temperature=0.9, 
                model="gpt-3.5-turbo", 
            )
        agent_memory = RoleMemory_GA(
            llm=chat_model,
            memory_retriever=memory_retriever,
            embedding_model=embedding_model,
            memory_decay_rate=0.01
        
        )
        return agent_memory
    
    else:
        db_name = kwargs["db_name"]
        embedding = kwargs["embedding"]
        db_type = kwargs["db_type"] if "db_type" in kwargs else "chromadb"
        capacity= kwargs["capacity"] if "capacity" in kwargs else 5
        agent_memory = RoleMemory(db_name=db_name,
                                  embedding=embedding,
                                  db_type=db_type,
                                  capacity=capacity)
        return agent_memory
        
def relevance_score_fn(score: float) -> float:
    return 1.0 - score / math.sqrt(2)

class RoleMemory_GA(GenerativeAgentMemory):
    def init_from_data(self,data):
        for text in data:
            self.add_record(text)
    
    def add_record(self,text):
        self.add_memory(text)
    
    def search(self,query,top_k):
        fetched_memories = [doc.page_content for doc in self.fetch_memories(query)[:top_k]]
        if len(fetched_memories)>=top_k:
            print("-Memory Searching...")
            print(fetched_memories)
        return fetched_memories
    
    def delete_record(self, idx):
        pass


class RoleMemory:
    def __init__(self,db_name,embedding,db_type = "chroma",capacity = 5,) -> None:
        self.idx = 0
        self.capacity = capacity
        self.db_name = db_name
        self.db = build_db([],db_name,db_type,embedding,save_type="temporary")
    
    def init_from_data(self,data):
        for text in data:
            self.add_record(text)
    
    def add_record(self,text):
        self.idx += 1
        self.db.add(text, str(self.idx), db_name=self.db_name)
    
    def search(self,query,top_k):
        return self.db.search(query, top_k,self.db_name)
    
    def delete_record(self, idx):
        self.db.delete(idx)
        
    @property
    def len(self):
        return self.db.len


