import time, hashlib
from huggingface_hub import InferenceClient
from app.config import settings

class HuggingFaceProvider:
    name = "huggingface"

    def __init__(self):
        self.client = InferenceClient(token=settings.hf_token)
        self.models = settings.model_list

    async def complete(self, messages: list, model: str, max_tokens: int = 512) -> dict:
        start = time.monotonic()

        # use chat_completion — works for all modern instruct models
        response = self.client.chat_completion(
            messages=messages,
            model=model,
            max_tokens=max_tokens,
            temperature=0.7,
        )
        latency = (time.monotonic() - start) * 1000

        text = response.choices[0].message.content

        input_tokens  = response.usage.prompt_tokens
        output_tokens = response.usage.completion_tokens

        prompt_str = " ".join(m["content"] for m in messages)

        return {
            "text":          text,
            "model":         model,
            "provider":      self.name,
            "input_tokens":  input_tokens,
            "output_tokens": output_tokens,
            "latency_ms":    latency,
            "prompt_hash":   hashlib.sha256(prompt_str.encode()).hexdigest(),
        }
