import re
import os
import docx
from datetime import datetime

from tqdm import tqdm

from graph import hg_client
from db import add_into_db, reset_index
from log import logger


def _add_graph_head(file_path, file_name, create_time):
    doc_node_id = hg_client.graph().addVertex(
        label="doc_node",
        properties={
            "file_path": file_path,
            "file_name": file_name,
            "create_time": create_time
        }
    ).id
    head_node_id = hg_client.graph().addVertex(
        label="para_node",
        properties={
            "file_path": file_path,
            "file_name": file_name,
            "content": "",
            "chunk_id": 0,
            "create_time": create_time
        }
    ).id
    hg_client.graph().addEdge(
        edge_label="doc_head",
        out_id=doc_node_id,
        in_id=head_node_id,
        properties={}
    )
    return head_node_id


def _add_graph_node(file_path, file_name, create_time, para, chunk_id, parent_id):
    node_id = hg_client.graph().addVertex(
        label="para_node",
        properties={
            "file_path": file_path,
            "file_name": file_name,
            "content": para.text,
            "chunk_id": chunk_id,
            "create_time": create_time
        }
    ).id
    hg_client.graph().addEdge(
        edge_label="para_para_down",
        out_id=parent_id,
        in_id=node_id,
        properties={}
    )
    return node_id


def load(file_path):
    file_name = os.path.basename(file_path)
    doc = docx.Document(file_path)
    create_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    heading_stack = []
    head_node_id = _add_graph_head(file_path, file_name, create_time)
    heading_stack.append((head_node_id, 0))
    data_to_db = []
    logger.info("Parsing docx...")
    for i, para in enumerate(tqdm(doc.paragraphs)):
        chunk_id = i + 1
        if re.match(r"Heading \d+$", para.style.name):
            heading_num = int(para.style.name[len("Heading "):])
            parent_id, parent_heading_num = heading_stack[-1]
            while heading_num <= parent_heading_num:
                heading_stack.pop()
                parent_id, parent_heading_num = heading_stack[-1]
            node_id = _add_graph_node(file_path, file_name, create_time, para, chunk_id, parent_id)
            data_to_db.append({"text": para.text, "node_id": node_id})
            heading_stack.append((node_id, heading_num))
        else:
            parent_id, _ = heading_stack[-1]
            node_id = _add_graph_node(file_path, file_name, create_time, para, chunk_id, parent_id)
            data_to_db.append({"text": para.text, "node_id": node_id})
    logger.info("Importing docx...")
    add_into_db(data_to_db)
    reset_index()


if __name__ == "__main__":
    from graph import init_graph
    init_graph()
    file_path = r"C:\Users\Vichayturen\Desktop\hust_article\03毕业论文\毕业论文-250310.docx"
    load(file_path)
