from .BaseLLM import BaseLLM
import requests
import json

class OllamaLLM(BaseLLM):
    def __init__(self, model="llama2"):
        super(OllamaLLM, self).__init__()
        self.model_name = model
        self.base_url = "http://localhost:11434/api"
        self.messages = []

    def initialize_message(self):
        self.messages = []

    def ai_message(self, payload):
        self.messages.append({"role": "assistant", "content": payload})

    def system_message(self, payload):
        self.messages.append({"role": "system", "content": payload})

    def user_message(self, payload):
        self.messages.append({"role": "user", "content": payload})

    def _format_messages(self):
        formatted_messages = []
        for msg in self.messages:
            role = msg["role"]
            content = msg["content"]
            if role == "system":
                formatted_messages.append({"role": "system", "content": content})
            elif role == "user":
                formatted_messages.append({"role": "user", "content": content})
            elif role == "assistant":
                formatted_messages.append({"role": "assistant", "content": content})
        return formatted_messages

    def get_response(self, temperature=0.8):
        """
        获取模型响应
        Args:
            temperature: 温度参数,控制响应的随机性
        Returns:
            模型的响应文本
        """
        messages = self._format_messages()
        
        # 准备请求数据
        data = {
            "model": self.model_name,
            "messages": messages,
            "stream": False,
            "options": {
                "temperature": temperature,
            }
        }

        try:
            # 发送POST请求到Ollama API
            response = requests.post(
                f"{self.base_url}/chat",
                json=data,
                headers={"Content-Type": "application/json"}
            )
            
            if response.status_code == 200:
                result = response.json()
                return result["message"]["content"]
            else:
                raise Exception(f"Error: {response.status_code}, {response.text}")
                
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to communicate with Ollama: {str(e)}")

    def chat(self, text, temperature=0.8):
        """
        单轮对话接口
        Args:
            text: 用户输入文本
            temperature: 温度参数
        Returns:
            模型的响应
        """
        self.initialize_message()
        self.user_message(text)
        return self.get_response(temperature=temperature)

    def print_prompt(self):
        """打印当前的对话历史"""
        for message in self.messages:
            print(message)

    def list_models(self):
        """获取可用模型列表"""
        try:
            response = requests.get(f"{self.base_url}/tags")
            if response.status_code == 200:
                return [model["name"] for model in response.json()["models"]]
            else:
                raise Exception(f"Error: {response.status_code}, {response.text}")
        except requests.exceptions.RequestException as e:
            raise Exception(f"Failed to get model list: {str(e)}")

    def stream_chat(self, text, temperature=0.8):
        """
        流式对话接口
        Args:
            text: 用户输入文本
            temperature: 温度参数
        Yields:
            生成的文本片段
        """
        messages = self._format_messages()
        
        data = {
            "model": self.model_name,
            "messages": messages,
            "stream": True,
            "options": {
                "temperature": temperature,
            }
        }

        try:
            response = requests.post(
                f"{self.base_url}/chat",
                json=data,
                headers={"Content-Type": "application/json"},
                stream=True
            )

            for line in response.iter_lines():
                if line:
                    json_response = json.loads(line)
                    if "message" in json_response:
                        yield json_response["message"]["content"]
                        
        except requests.exceptions.RequestException as e:
            raise Exception(f"Streaming failed: {str(e)}")
