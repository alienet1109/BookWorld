from .BaseLLM import BaseLLM
from openai import OpenAI
import os

class DeepSeek(BaseLLM):
    
    def __init__(self, model="deepseek-chat"):
        super(DeepSeek, self).__init__()
        self.client = OpenAI(
        api_key=os.getenv("DEEPSEEK_API_KEY"), 
        base_url="https://api.deepseek.com",
    )
        self.model_name = model
        self.messages = []


    def initialize_message(self):
        self.messages = []

    def ai_message(self, payload):
        self.messages.append({"role": "ai", "content": payload})

    def system_message(self, payload):
        self.messages.append({"role": "system", "content": payload})

    def user_message(self, payload):
        self.messages.append({"role": "user", "content": payload})

    def get_response(self,temperature = 0.8):
    
        response = self.client.chat.completions.create(
        model="deepseek-chat",
        messages=self.messages,
        stream=False
)
        return response.choices[0].message.content
    
    def chat(self,text):
        self.initialize_message()
        self.user_message(text)
        response = self.get_response()
        return response
    
    def print_prompt(self):
        for message in self.messages:
            print(message)