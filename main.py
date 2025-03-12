
import traceback

import gradio as gr
import pandas as pd

from graph import hg_client, init_or_reset_graph
from loader import load
from db import init_or_reset_db, query_db
from llm import chat
from prompt import get_rag_prompt


def gremlin_query(vid):
    return f"""\
g.V({vid}).union(
    __.identity(),
    __.repeat(
       outE('para_para_down').limit(10).otherV().dedup()
    ).times(3).emit()
).order().by('chunk_id', asc)
"""


def rag_query(query: str):
    try:
        fts_result = query_db(query)
        print(fts_result)
        final_result = []
        for item in fts_result:
            node_id = item["node_id"]
            nodes = hg_client.gremlin().exec(gremlin_query(node_id))
            combined_content = "\n".join([u["properties"]["content"] for u in nodes["data"]])
            combined_chunk_ids = ",".join([str(u["properties"]["chunk_id"]) for u in nodes["data"]])
            final_result.append({
                "start_node_id": node_id,
                "combined_content": combined_content,
                "nodes": combined_chunk_ids
            })
        prompt = get_rag_prompt(query, [u["combined_content"] for u in final_result])
        answer = chat(prompt)
        return pd.DataFrame(final_result), prompt, answer
    except Exception as e:
        traceback.print_exc()
        gr.Error(e)


def main():
    with gr.Blocks() as demo:
        btn = gr.Button("清空图数据并构建图schema")
        def gr_init_or_reset_graph():
            try:
                init_or_reset_graph()
                gr.Info("Success!")
            except Exception as e:
                traceback.print_exc()
                gr.Error(e)
        btn.click(gr_init_or_reset_graph)
        btn2 = gr.Button("清空向量数据库数据并构建表schema")
        def gr_init_or_reset_db():
            try:
                init_or_reset_db()
                gr.Info("Success!")
            except Exception as e:
                traceback.print_exc()
                gr.Error(e)
        btn2.click(gr_init_or_reset_db)
        file_box = gr.File(label="Document")
        upload_btn = gr.Button("Upload")
        def gr_upload(file):
            file_path = file.name
            try:
                load(file_path)
                gr.Info("Success!")
                return None
            except Exception as e:
                traceback.print_exc()
                gr.Error(e)
        upload_btn.click(gr_upload, inputs=file_box, outputs=file_box)
        query_box = gr.Textbox(label="Query")
        query_btn = gr.Button("Query")
        search_result_box = gr.Dataframe(label="Search Result")
        prompt_box = gr.Textbox(label="Prompt")
        answer_box = gr.Markdown(label="Answer")
        def gr_rag_query(query):
            try:
                res = rag_query(query)
                gr.Info("Success!")
                return res
            except Exception as e:
                traceback.print_exc()
                gr.Error(e)
        query_btn.click(gr_rag_query, inputs=query_box, outputs=[search_result_box, prompt_box, answer_box])

    demo.launch(server_name="0.0.0.0")


if __name__ == "__main__":
    main()
