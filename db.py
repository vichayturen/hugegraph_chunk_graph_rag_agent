from typing import List, Dict, Any

import lancedb
import pyarrow as pa
from tqdm import tqdm

from llm import embed
from config import LLMConfig


def add_into_db(rows: List[Dict[str, Any]]):
    db = lancedb.connect("~/.lancedb")
    table_name = "graphrag"
    table = db.open_table(table_name)
    batch_size = 20
    tbar = tqdm(total=len(rows))
    for i in range(0, len(rows), batch_size):
        now_rows = rows[i:min(i + batch_size, len(rows))]
        vectors = embed([item["text"] for item in now_rows])
        for row, vector in zip(now_rows, vectors):
            row["vector"] = vector
        table.add(now_rows)
        tbar.update(len(now_rows))
    tbar.close()


def reset_index():
    db = lancedb.connect("~/.lancedb")
    table_name = "graphrag"
    table = db.open_table(table_name)
    # table.create_fts_index("text", replace=True)
    table.create_index("L2", replace=True)


def query_db(query: str, topk: int = 10) -> list:
    db = lancedb.connect("~/.lancedb")
    table_name = "graphrag"
    table = db.open_table(table_name)
    res = table.search(embed(query)[0]).select(["node_id"]).limit(topk).to_list()
    # res = table.search(query, query_type="fts").limit(topk).select(["node_id"]).to_list()
    return res


def init_or_reset_db():
    db = lancedb.connect("~/.lancedb")
    table_name = "graphrag"
    if table_name in db.table_names():
        db.drop_table(table_name)
    schema = pa.schema([
        pa.field("text", pa.utf8()),
        pa.field("vector", pa.list_(pa.float32(), LLMConfig.embedding_size)),
        pa.field("node_id", pa.utf8()),
    ])
    db.create_table(
        name=table_name,
        schema=schema,
    )
    # table.create_fts_index("text", replace=True)
    # table.create_index("cosine", replace=True)
