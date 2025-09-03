import sys
sys.path.append("../")
from chromadb.api.types import Embeddings, Documents, EmbeddingFunction, Space
from modelscope import AutoModel, AutoTokenizer
from functools import partial
from bw_utils import get_child_folders
import torch
import os


class EmbeddingModel(EmbeddingFunction[Documents]):
    def __init__(self, model_name, language='en'):
        self.model_name = model_name
        self.language = language
        cache_dir = "~/.cache/modelscope/hub"
        model_provider = model_name.split("/")[0]
        model_smallname = model_name.split("/")[1]
        model_path = os.path.join(cache_dir, f"models--{model_provider}--{model_smallname}/snapshots/")
        
        if os.path.exists(model_path) and get_child_folders(model_path):
            try:
                model_path = os.path.join(model_path,get_child_folders(model_path)[0])
                self.tokenizer = AutoTokenizer.from_pretrained(model_path)
                self.model = AutoModel.from_pretrained(model_path)
            except Exception as e:
                print(e)
                self.tokenizer = AutoTokenizer.from_pretrained(model_name)
                self.model = AutoModel.from_pretrained(model_name)
        else:
            self.tokenizer = AutoTokenizer.from_pretrained(model_name)
            self.model = AutoModel.from_pretrained(model_name)

    def __call__(self, input):
        inputs = self.tokenizer(input, return_tensors="pt", padding=True, truncation=True, max_length=256)
        with torch.no_grad():
            outputs = self.model(**inputs)
        embeddings = outputs.last_hidden_state[:, 0, :].tolist()
        return embeddings

class OpenAIEmbedding(EmbeddingFunction[Documents]):
    def __init__(self, model_name="text-embedding-ada-002", base_url = "https://api.openai.com/v1/embeddings", api_key_field = "OPENAI_API_KEY"):
        from openai import OpenAI
            
        self.client = OpenAI(
            base_url = base_url,
            api_key = os.environ[api_key_field]
        )
        self.model_name = model_name

    def __call__(self, input):
        if isinstance(input, str):
            input = input.replace("\n", " ")
            return self.client.embeddings.create(input=[input], model=self.model_name).data[0].embedding
        elif isinstance(input,list):
            return [self.client.embeddings.create(input=[sentence.replace("\n", " ")], model=self.model_name).data[0].embedding for sentence in input]
def get_embedding_model(embed_name, language='en'):
    local_model_dict = {
        "bge-m3":"BAAI/bge-m3",
        "bge-large": f"BAAI/bge-large-{language}",
        "luotuo": "silk-road/luotuo-bert-medium",
        "bert": "google-bert/bert-base-multilingual-cased",
        "bge-small": f"BAAI/bge-small-{language}",
    }
    online_model_dict = {
        "openai":
            {"model_name":"text-embedding-ada-002",
             "url":"https://api.openai.com/v1/embeddings",
             "api_key_field":"OPENAI_API_KEY"},

    }
    if embed_name in online_model_dict:
        model_name = online_model_dict[embed_name]["model_name"]
        api_key_field = online_model_dict[embed_name]["api_key_field"]
        base_url = online_model_dict[embed_name]["url"]
        return OpenAIEmbedding(model_name=model_name, base_url=base_url,api_key_field=api_key_field)

