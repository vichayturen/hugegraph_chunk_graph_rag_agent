from typing import List

import requests
from litellm import completion, embedding

from config import LLMConfig, OllamaConfig, LiteLLmConfig


def litellm_chat(prompt: str):
    response = completion(
        model=LiteLLmConfig.model,
        messages=[{"content": prompt,"role": "user"}], 
        api_base=LiteLLmConfig.api_base,
        api_key=LiteLLmConfig.api_key
    )
    return response.choices[0].message.content


def litellm_embed(text: str | List[str]):
    if isinstance(text, str):
        text = [text]
    response = embedding(
        model=LiteLLmConfig.embedding_model,
        input=text,
        api_base=LiteLLmConfig.api_base,
        api_key=LiteLLmConfig.api_key
    )
    return [u["embedding"] for u in response.data]


def ollama_embed(text: str | List[str]):
    if isinstance(text, str):
        text = [text]
    response = requests.post(
        url=OllamaConfig.url + "/api/embed",
        json={
            "model": OllamaConfig.embedding_model,
            "input": text,
        }
    )
    return response.json()["embeddings"]


def ollama_chat(prompt: str):
    response = requests.post(
        url=OllamaConfig.url + "/api/chat",
        json={
            "model": OllamaConfig.model,
            "messages": [
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            "stream": False
        }
    )
    return response.json()["message"]["content"]


if LLMConfig.use_llm == "ollama":
    chat = ollama_chat
    embed = ollama_embed
elif LLMConfig.use_llm == "litellm":
    chat = litellm_chat
    embed = litellm_embed
elif LLMConfig.use_llm == "openai":
    chat = litellm_chat
    embed = litellm_embed
else:
    raise ValueError


if __name__ == "__main__":
    res = ollama_embed(["你是谁？", "你好"])
    print(res)
    print(len(res))
