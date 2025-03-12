from typing import Literal


class HugeGraphConfig:
    ip = "192.168.21.105"
    port = "18080"
    graph = "hugegraph"
    user = "admin"
    pwd = "xxx"


class LLMConfig:
    use_llm: Literal["openai", "ollama", "litellm"] = "ollama"
    embedding_size = 1024


class LiteLLmConfig:
    api_key = "xxx"
    api_base = "http://192.168.21.105:11434"
    model = "ollama/qwen2.5:3b-instruct-fp16"
    embedding_model = "ollama/bge-m3"


class OpenAIConfig:
    api_key = "xxx"
    api_base = "http://192.168.21.105:11434/v1"
    model = "ollama/qwen2.5:3b-instruct-fp16"
    embedding_model = "ollama/bge-m3"


class OllamaConfig:
    url = "http://192.168.21.105:11434"
    model = "qwen2.5:3b-instruct-fp16"
    embedding_model = "bge-m3"
