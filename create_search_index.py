import os
import argparse
import uuid

from azure.ai.projects import AIProjectClient
from azure.ai.projects.models import ConnectionType
from azure.identity import DefaultAzureCredential
from azure.core.credentials import AzureKeyCredential
from azure.search.documents import SearchClient
from azure.search.documents.indexes import SearchIndexClient
from config import get_logger
from docx import Document
from pathlib import Path


import pandas as pd
from azure.search.documents.indexes.models import (
    SemanticSearch,
    SearchField,
    SimpleField,
    SearchableField,
    SearchFieldDataType,
    SemanticConfiguration,
    SemanticPrioritizedFields,
    SemanticField,
    VectorSearch,
    HnswAlgorithmConfiguration,
    VectorSearchAlgorithmKind,
    HnswParameters,
    VectorSearchAlgorithmMetric,
    ExhaustiveKnnAlgorithmConfiguration,
    ExhaustiveKnnParameters,
    VectorSearchProfile,
    SearchIndex,
)

# initialize logging object
logger = get_logger(__name__)

project = AIProjectClient.from_connection_string(
        conn_str=os.environ["AIPROJECT_CONNECTION_STRING"], credential=DefaultAzureCredential()
)
# create a vector embeddings client that will be used to generate vector embeddings
embeddings = project.inference.get_embeddings_client()

# use the project client to get the default search connection
search_connection = project.connections.get_default(
    connection_type=ConnectionType.AZURE_AI_SEARCH, include_credentials=True
)

# Create a search index client using the search connection
# This client will be used to create and delete search indexes
index_client = SearchIndexClient(
    endpoint=search_connection.endpoint_url, credential=AzureKeyCredential(key=search_connection.key)
)


def create_index_definition(index_name: str, model: str) -> SearchIndex:
    dimensions = 1536  # text-embedding-ada-002
    if model == "text-embedding-3-large":
        dimensions = 3072

    # The fields we want to index. The "embedding" field is a vector field that will
    # be used for vector search.
    fields = [
        SimpleField(name="id", type=SearchFieldDataType.String, key=True),
        SearchableField(name="content", type=SearchFieldDataType.String),
        SimpleField(name="filepath", type=SearchFieldDataType.String),
        SearchableField(name="title", type=SearchFieldDataType.String),
        SimpleField(name="url", type=SearchFieldDataType.String),
        SearchField(
            name="contentVector",
            type=SearchFieldDataType.Collection(SearchFieldDataType.Single),
            searchable=True,
            # Size of the vector created by the text-embedding-ada-002 model.
            vector_search_dimensions=dimensions,
            vector_search_profile_name="myHnswProfile",
        ),
    ]

    # The "content" field should be prioritized for semantic ranking.
    semantic_config = SemanticConfiguration(
        name="default",
        prioritized_fields=SemanticPrioritizedFields(
            title_field=SemanticField(field_name="title"),
            keywords_fields=[],
            content_fields=[SemanticField(field_name="content")],
        ),
    )

    # For vector search, we want to use the HNSW (Hierarchical Navigable Small World)
    # algorithm (a type of approximate nearest neighbor search algorithm) with cosine
    # distance.
    vector_search = VectorSearch(
        algorithms=[
            HnswAlgorithmConfiguration(
                name="myHnsw",
                kind=VectorSearchAlgorithmKind.HNSW,
                parameters=HnswParameters(
                    m=4,
                    ef_construction=1000,
                    ef_search=1000,
                    metric=VectorSearchAlgorithmMetric.COSINE,
                ),
            ),
            ExhaustiveKnnAlgorithmConfiguration(
                name="myExhaustiveKnn",
                kind=VectorSearchAlgorithmKind.EXHAUSTIVE_KNN,
                parameters=ExhaustiveKnnParameters(metric=VectorSearchAlgorithmMetric.COSINE),
            ),
        ],
        profiles=[
            VectorSearchProfile(
                name="myHnswProfile",
                algorithm_configuration_name="myHnsw",
            ),
            VectorSearchProfile(
                name="myExhaustiveKnnProfile",
                algorithm_configuration_name="myExhaustiveKnn",
            ),
        ],
    )

    # Create the semantic settings with the configuration
    semantic_search = SemanticSearch(configurations=[semantic_config])

    # Create the search index definition
    return SearchIndex(
        name=index_name,
        fields=fields,
        semantic_search=semantic_search,
        vector_search=vector_search,
    )

def read_docx(path: str) -> str:
    doc = Document(path)
    paragraphs = [p.text.strip() for p in doc.paragraphs if p.text.strip()]
    return "\n".join(paragraphs)

def chunk_text(text: str, chunk_size: int = 800, overlap: int = 100) -> list[str]:
    """Split into ~``chunk_size``-char chunks at spaces; overlap carries across chunks."""
    n = len(text)

    def exclusive_end(lo: int, cap: int) -> int:
        """Index after chunk text: last space before ``cap``, or next space if no word fits."""
        if cap >= n:
            return n
        last = text.rfind(" ", lo + 1, cap)
        if last > lo:
            return last
        nxt = text.find(" ", cap)
        return nxt if nxt != -1 else n

    chunks: list[str] = []
    i = 0
    while i < n:
        while i < n and text[i].isspace():
            i += 1
        if i >= n:
            break
        j = exclusive_end(i, min(i + chunk_size, n))
        piece = text[i:j].strip()
        if piece:
            chunks.append(piece)
        if j >= n:
            break
        nxt = j - overlap
        if nxt <= i:
            nxt = j + 1
        else:
            sp = text.rfind(" ", i, nxt + 1)
            if sp >= i:
                nxt = sp + 1
        i = nxt
    return chunks

def create_docs_from_docx(
    docx_paths: list[str],
    model: str,
) -> list[dict[str, any]]:
    items = []

    for path in docx_paths:
        full_text = read_docx(path)
        chunks = chunk_text(full_text)

        title = Path(path).stem.replace("_", " ").title()

        for i, chunk in enumerate(chunks):
            emb = embeddings.embed(input=chunk, model=model)

            rec = {
                "id": str(uuid.uuid4()),
                "content": chunk,
                "filepath": path,
                "title": title,
                "url": f"/docs/{Path(path).name}",
                "contentVector": emb.data[0].embedding,
            }
            items.append(rec)

    return items


def create_index_from_docx(index_name: str, docx_files: list[str]):
    # Delete index if it exists
    try:
        index_client.get_index(index_name)
        index_client.delete_index(index_name)
        logger.info(f"🗑️ Deleted existing index '{index_name}'")
    except Exception:
        pass

    # Create index
    index_definition = create_index_definition(
        index_name, model=os.environ["EMBEDDINGS_MODEL"]
    )
    index_client.create_index(index_definition)

    # Create documents from DOCX
    docs = create_docs_from_docx(
        docx_paths=docx_files,
        model=os.environ["EMBEDDINGS_MODEL"],
    )

    # Upload documents
    search_client = SearchClient(
        endpoint=search_connection.endpoint_url,
        index_name=index_name,
        credential=AzureKeyCredential(key=search_connection.key),
    )

    search_client.upload_documents(docs)
    logger.info(f"➕ Uploaded {len(docs)} chunks to '{index_name}'")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--index-name",
        type=str,
        default=os.environ["AISEARCH_INDEX_NAME"],
    )
    parser.add_argument(
        "--docx-files",
        nargs="+",
        default=[
            "assets/employee_handbook.docx",
            "assets/leave_policy.docx",
        ],
        help="List of DOCX files to index",
    )

    args = parser.parse_args()

    create_index_from_docx(
        index_name=args.index_name,
        docx_files=args.docx_files,
    )
    
if __name__ == "__main__":
    main()

