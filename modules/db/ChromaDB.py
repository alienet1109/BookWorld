import chromadb
from .BaseDB import BaseDB
import os
from tqdm import tqdm
import uuid

class ChromaDB(BaseDB):
    def __init__(self, embedding, save_type="persistent"):
        try:
            self.collections = {}
            self.embedding = embedding

            base_dir = os.path.dirname(os.path.abspath(__file__))
            if save_type == "persistent":
                self.path = os.path.join(base_dir, "./chromadb_saves/")
                os.makedirs(self.path, exist_ok=True)
                self.client = chromadb.PersistentClient(path=self.path)
            else:
                self.client = chromadb.Client()
        except Exception as e:
            raise Exception(f"Failed to initialize ChromaDB: {str(e)}")

    def init_from_data(self, data, db_name):
        if not db_name:
            raise ValueError("Invalid db_name")
        if not data:
            collection = self.client.get_collection(
                    name=db_name,
                    embedding_function=self.embedding
                )
            self.collections[db_name] = collection
        try:
            new_data_set = set(data)
            if db_name in [c.name for c in self.client.list_collections()]:
                collection = self.client.get_collection(
                    name=db_name,
                    embedding_function=self.embedding
                )
                self.collections[db_name] = collection
                
                # 获取现有collection中的所有数据
                existing_data = collection.get()
                existing_docs = existing_data['documents']
                existing_ids = existing_data['ids']
                
                # 创建现有文档的映射 {文档内容: ID}
                existing_doc_map = {doc: id_ for doc, id_ in zip(existing_docs, existing_ids)}
                
                # 找出需要删除的文档（在现有数据中但不在新数据中的）
                docs_to_delete = [id_ for doc, id_ in existing_doc_map.items() 
                                if doc not in new_data_set]
                if docs_to_delete:
                    collection.delete(ids=docs_to_delete)
                
                # 找出需要添加的文档（在新数据中但不在现有数据中的）
                docs_to_add = [doc for doc in new_data_set 
                            if doc not in existing_doc_map]
                
                # 批量添加新文档
                if docs_to_add:
                    new_ids = [str(uuid.uuid4()) for _ in range(len(docs_to_add))]
                    collection.add(
                        documents=docs_to_add,
                        ids=new_ids
                    )
                    
            else:
                collection = self.client.create_collection(
                    name=db_name,
                    embedding_function=self.embedding
                )
                self.collections[db_name] = collection
                
                ids = [str(uuid.uuid4()) for _ in range(len(data))]
                collection.add(
                    documents=data,
                    ids=ids
                )
            
        except Exception as e:
            raise Exception(f"Failed to initialize data: {str(e)}")


    def search(self, query, n_results, db_name):
        if not query or not db_name or db_name not in self.collections:
            return []
        
        try:
            n_results = min(self.collections[db_name].count(), n_results)
            if n_results < 1:
                return []
            results = self.collections[db_name].query(
                query_texts=[query], 
                n_results=n_results
            )
            return results['documents'][0]
        except Exception as e:
            print(f"Search error: {str(e)}")
            return []

    def check_text_exists(self, text, collection):
        """检查文本是否已存在于集合中"""
        try:
            results = collection.query(
                query_texts=[text],
                n_results=1
            )
            print(results)
            return bool(results['documents'][0] and results['documents'][0][0] == text)
        except Exception:
            return False

    def find_text_id(self, text, collection):
        """查找与给定文本匹配的ID"""
        try:
            all_data = collection.get()
            for i, doc in enumerate(all_data['documents']):
                if doc == text:
                    return all_data['ids'][i]
            return None
        except Exception:
            return None

    def add(self, text, db_name=""):
        if not text:
            raise ValueError("Text cannot be empty")

        try:
            if db_name not in self.collections:
                self.collections[db_name] = self.client.get_or_create_collection(
                    name=db_name,
                    embedding_function=self.embedding
                )

            collection = self.collections[db_name]

            if not self.check_text_exists(text, collection):
                new_id = str(uuid.uuid4())
                collection.add(
                    documents=[text],
                    ids=[new_id]
                )
                return True  
            return False  
        except Exception as e:
            raise Exception(f"Failed to add document: {str(e)}")

    def delete(self, text, db_name):
        if not text or not db_name or db_name not in self.collections:
            return False

        try:
            collection = self.collections[db_name]
            text_id = self.find_text_id(text, collection)
            
            if text_id:
                collection.delete(ids=[text_id])
                return True 
            return False 
        except Exception as e:
            print(f"Delete error: {str(e)}")
            return False
