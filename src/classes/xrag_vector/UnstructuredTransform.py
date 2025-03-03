from llama_index.core.ingestion import IngestionPipeline
from llama_index.core.node_parser import JSONNodeParser
from llama_index.core.schema import TransformComponent


class UnstructuredTransform(TransformComponent):
    def __call__(self, docs, **kwargs):
        pipeline = IngestionPipeline(transformations=[JSONNodeParser()])
        base_nodes = pipeline.run(documents=docs, show_progress=True)
        return base_nodes
