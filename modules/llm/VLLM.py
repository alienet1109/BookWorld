from .BaseLLM import BaseLLM
from vllm import LLM, SamplingParams

class LocalVLLM(BaseLLM):
    def init(
    self,
    model, 
    tensor_parallel_size=1,
    trust_remote_code=False,
    dtype="auto",
    max_model_len=None,
    gpu_memory_utilization=0.90,
    seed=None,
    enforce_eager=False,
    **llm_kwargs
    ):
        super(LocalVLLM, self).init()
        self.model_name = model
        self.messages = []
        self.llm = LLM(
        model=model,
        tensor_parallel_size=tensor_parallel_size,
        trust_remote_code=trust_remote_code,
        dtype=dtype,
        max_model_len=max_model_len,
        gpu_memory_utilization=gpu_memory_utilization,
        seed=seed,
        enforce_eager=enforce_eager,
        **llm_kwargs
        )
        self.tokenizer = self.llm.get_tokenizer()

    def initialize_message(self):
        self.messages = []

    def ai_message(self, payload):
        self.messages.append({"role": "assistant", "content": payload})

    def system_message(self, payload):
        self.messages.append({"role": "system", "content": payload})

    def user_message(self, payload):
        self.messages.append({"role": "user", "content": payload})

    def _convert_roles_for_chat_template(self, messages=None):
        if messages is None:
            messages = self.messages
        converted = []
        for m in messages:
            role = m.get("role", "user")
            converted.append({"role": role, "content": m.get("content", "")})
        return converted

    def _build_prompt(self, messages=None):
        """
        将 role-based messages 转为模型可用的字符串 prompt。
        优先使用 tokenizer.apply_chat_template；
        若模型无 chat_template，则回退到简单的格式化串。
        """
        conv = self._convert_roles_for_chat_template(messages)
        try:
            # 对于带有 chat template 的指令微调模型（如 Llama-3-Instruct、Qwen、Mistral-Instruct 等）
            prompt = self.tokenizer.apply_chat_template(
                conv,
                tokenize=False,
                add_generation_prompt=True
            )
        except Exception:
            # 回退方案：简单串接（可能不如 chat template 效果好）
            lines = []
            for m in conv:
                if m["role"] == "system":
                    lines.append(f"<<SYS>>\n{m['content']}\n<</SYS>>")
                elif m["role"] == "user":
                    lines.append(f"User: {m['content']}")
                elif m["role"] == "assistant":
                    lines.append(f"Assistant: {m['content']}")
                else:
                    lines.append(f"{m['role'].capitalize()}: {m['content']}")
            lines.append("Assistant: ")
            prompt = "\n".join(lines)
        return prompt

    def get_response(
        self,
        temperature=0.8,
        top_p=0.8,
        max_tokens=1024,
        stop=None
    ):
        prompt = self._build_prompt(self.messages)
        sampling_params = SamplingParams(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop=stop
        )
        outputs = self.llm.generate([prompt], sampling_params)
        text = outputs[0].outputs[0].text if outputs and outputs[0].outputs else ""
        return text.strip()

    def chat(self, text, temperature=0.8, top_p=0.8, max_tokens=1024, stop=None):
        self.initialize_message()
        self.user_message(text)
        response = self.get_response(
            temperature=temperature,
            top_p=top_p,
            max_tokens=max_tokens,
            stop=stop
        )
        return response

    def print_prompt(self):
        for message in self.messages:
            print(message)
        print("----- Rendered Prompt -----")
        print(self._build_prompt(self.messages))