import chromadb
from .BaseDB import BaseDB
import random
import string
import os
from tqdm import tqdm

class ChromaDB(BaseDB):
    
    def __init__(self,embedding,save_type = "persistent"):
        self.collections = {}
        self.embedding = embedding

        base_dir = os.path.dirname(os.path.abspath(__file__))
        if save_type == "persistent":
            self.path = os.path.join(base_dir, "./chromadb_saves/")
            self.client = chromadb.PersistentClient(path = self.path)
        else:
            self.client = chromadb.Client()

    def init_from_data(self, data, db_name):
        if db_name in [c.name for c in self.client.list_collections()]:
            self.collections[db_name] = self.client.get_collection(name=db_name,embedding_function=self.embedding)
        else:
            self.collections[db_name] = self.client.create_collection(name=db_name,embedding_function=self.embedding)
            if len(data) != 0:
                for i in  tqdm(list(range(self.collections[db_name].count()+1,len(data)))):
                    self.collections[db_name].add(
                        documents=[data[i]],
                        ids=[str(i)]
                    )
        return 

    def search(self, query, n_results, db_name):
        if db_name not in self.collections:return []
        n_results = min(self.collections[db_name].count(), n_results)
        if n_results < 1:
            return []
        results = self.collections[db_name].query(query_texts=[query], n_results=n_results)
        return results['documents'][0]
    
    def add(self,text,idx, db_name=""):
        if db_name not in self.collections:
            self.collections[db_name] = self.client.create_collection(
                name=db_name,
                embedding_function=self.embedding
            )
            self.collections[db_name].add(
                documents=[text],
                ids=[idx]
            )
            return

        collection = self.collections[db_name]

        existing_doc = collection.get(ids=[idx])

        if existing_doc and existing_doc['ids']:
            collection.update(
                documents=[text],
                ids=[idx]
            )
        else:
            collection.add(
                documents=[text],
                ids=[idx]
            )
    def delete(self,idx,db_name):
        self.collections[db_name].delete(ids=[idx])


