# app/providers/huggingface.py
import httpx, time, hashlib
from app.config import settings

HF_API = "https://api-inference.huggingface.co/models"

class HuggingFaceProvider:
    name = "huggingface"

    def __init__(self):
        self.headers = {"Authorization": f"Bearer {settings.hf_token}"}
        self.models  = settings.model_list

    async def complete(self, messages: list, model: str, max_tokens: int = 512) -> dict:
        prompt = self._format_messages(messages)
        payload = {
            "inputs": prompt,
            "parameters": {
                "max_new_tokens": max_tokens,
                "temperature": 0.7,
                "return_full_text": False,
            }
        }
        start = time.monotonic()
        async with httpx.AsyncClient(timeout=60) as client:
            r = await client.post(
                f"{HF_API}/{model}",
                headers=self.headers,
                json=payload
            )
            r.raise_for_status()

        data = r.json()
        text = data[0]["generated_text"] if isinstance(data, list) else data.get("generated_text", "")
        latency = (time.monotonic() - start) * 1000

        input_tokens  = len(prompt.split())        # rough estimate
        output_tokens = len(text.split())

        return {
            "text": text,
            "model": model,
            "provider": self.name,
            "input_tokens": input_tokens,
            "output_tokens": output_tokens,
            "latency_ms": latency,
            "prompt_hash": hashlib.sha256(prompt.encode()).hexdigest(),
        }

    def _format_messages(self, messages: list) -> str:
        parts = []
        for m in messages:
            role    = m["role"].capitalize()
            content = m["content"]
            parts.append(f"<|{role}|>\n{content}")
        parts.append("<|Assistant|>")
        return "\n".join(parts)