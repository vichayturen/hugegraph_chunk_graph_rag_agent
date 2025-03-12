def get_rag_prompt(query: str, result: list) -> str:
    prompt = """\
请你仔细阅读以下上下文，参考其内容来回答最后的问题。
{}

Question: {}\
""".format("\n".join([f"({i+1}) {str(item)}" for i, item in enumerate(result)]), query)
    return prompt
