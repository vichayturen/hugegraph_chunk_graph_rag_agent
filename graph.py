import pyhugegraph.client

from config import HugeGraphConfig


hg_client = pyhugegraph.client.PyHugeClient(
    ip=HugeGraphConfig.ip,
    port=HugeGraphConfig.port,
    graph=HugeGraphConfig.graph,
    user=HugeGraphConfig.user,
    pwd=HugeGraphConfig.pwd,
)


def init_or_reset_graph():
    hg_client.graphs().clear_graph_all_data()
    schema = hg_client.schema()
    schema.propertyKey("file_path").asText().ifNotExist().create()
    schema.propertyKey("file_name").asText().ifNotExist().create()
    schema.propertyKey("content").asText().ifNotExist().create()
    schema.propertyKey("chunk_id").asLong().ifNotExist().create()
    schema.propertyKey("create_time").asText().ifNotExist().create()
    schema.vertexLabel("doc_node").useAutomaticId().properties(
        "file_path", "file_name", "create_time").ifNotExist().create()
    schema.vertexLabel("para_node").useAutomaticId().properties(
        "file_path", "file_name", "content", "chunk_id", "create_time").ifNotExist().create()
    schema.edgeLabel("para_para_down").sourceLabel("para_node").targetLabel(
        "para_node").properties().ifNotExist().create()
    schema.edgeLabel("doc_head").sourceLabel("doc_node").targetLabel(
        "para_node").properties().ifNotExist().create()
