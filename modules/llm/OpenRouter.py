from .BaseLLM import BaseLLM
import os
from openai import OpenAI
import tiktoken
encoding = tiktoken.encoding_for_model("gpt-4o")

class OpenRouter(BaseLLM):
    def __init__(self, model="deepseek/deepseek-r1:free"):
        super(OpenRouter, self).__init__()
        self.client = OpenAI(
        api_key=os.getenv("OPENROUTER_API_KEY"), 
        base_url="https://openrouter.ai/api/v1",
        )
        self.model_name = model
        self.messages = []
        self.in_token = 0
        self.out_token = 0
    def initialize_message(self):
        self.messages = []

    def ai_message(self, payload):
        self.messages.append({"role": "ai", "content": payload})

    def system_message(self, payload):
        self.messages.append({"role": "system", "content": payload})

    def user_message(self, payload):
        self.messages.append({"role": "user", "content": payload})

    def get_response(self,temperature = 0.8):
        completion = self.client.chat.completions.create(
            model=self.model_name,
            messages=self.messages
            )
        return completion.choices[0].message.content
    
    def chat(self,text,temperature = 0.8):
        self.initialize_message()
        self.user_message(text)
        response = self.get_response(temperature = temperature)
        self.in_token += self.count_token(text)
        self.out_token += self.count_token(response)
        return response
    
    def print_prompt(self):
        for message in self.messages:
            print(message)
    def count_token(self,text,):
        return len(encoding.encode(text))