from .BaseLLM import BaseLLM
from google import genai
import os
import time

class Gemini(BaseLLM):
    def __init__(self, model="gemini-2.0-flash"):
        super(Gemini, self).__init__()
        self.model_name = model
        self.messages = []


    def initialize_message(self):
        self.messages = []

    def ai_message(self, payload):
        self.messages.append(payload)

    def system_message(self, payload):
        self.messages.append(payload)

    def user_message(self, payload):
        self.messages.append(payload)

    def get_response(self,temperature = 0.8):
        response = genai.Client(api_key=os.getenv("GEMINI_API_KEY")).models.generate_content(
        model=self.model_name, contents="".join(self.messages), temperature = temperature
        )
        return response.text
    
    def chat(self,text):
        self.initialize_message()
        self.user_message(text)
        response = self.get_response()
        
        return response
    
    def print_prompt(self):
        for message in self.messages:
            print(message)