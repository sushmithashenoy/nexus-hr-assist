import os
from pathlib import Path
from azure.ai.projects import AIProjectClient
from azure.identity import DefaultAzureCredential
from config import ASSET_PATH, get_logger
from get_sub_documents import get_sub_documents


# initialize logging and tracing objects
logger = get_logger(__name__)

# create a project client using environment variables loaded from the .env file
project = AIProjectClient.from_connection_string(
    conn_str=os.environ["AIPROJECT_CONNECTION_STRING"], credential=DefaultAzureCredential()
)

# create a chat client we can use for testing
chat = project.inference.get_chat_completions_client()

from azure.ai.inference.prompts import PromptTemplate

# Cap how much prior chat we send to stay within model context limits.
_MAX_CONVERSATION_MESSAGES = 40


def _trim_conversation(messages: list[dict]) -> list[dict]:
    if len(messages) <= _MAX_CONVERSATION_MESSAGES:
        return messages
    return messages[-_MAX_CONVERSATION_MESSAGES :]


def chat_with_sub_documents(messages: list, context: dict = None) -> dict:
    if context is None:
        context = {}

    documents = get_sub_documents(messages, context)

    # do a grounded chat call using the search results
    grounded_chat_prompt = PromptTemplate.from_prompty(Path(ASSET_PATH) / "grounded_chat.prompty")

    system_message = grounded_chat_prompt.create_messages(documents=documents, context=context)
    response = chat.complete(
        model=os.environ["CHAT_MODEL"],
        messages=system_message + messages,
        **grounded_chat_prompt.parameters,
    )
    logger.info(f"💬{response.choices[0].message.content}")

    # Return a chat protocol compliant response
    return {"message": response.choices[0].message, "context": context}


def run_chat(query: str | None = None, messages: list[dict] | None = None) -> dict:
    """Run grounded HR chat and return a JSON-serializable result for APIs and UIs.

    Pass either ``messages`` (full thread, last turn should be the current user message)
    or ``query`` for a single-turn request (backward compatible).
    """
    if messages:
        msgs = _trim_conversation([dict(m) for m in messages])
    else:
        q = (query or "").strip()
        msgs = [{"role": "user", "content": q}]
    result = chat_with_sub_documents(messages=msgs)
    msg = result["message"]
    ctx = result["context"]

    documents: list[dict] = []
    for batch in ctx.get("grounding_data") or []:
        documents.extend(batch)

    seen: set[str] = set()
    unique_docs: list[dict] = []
    for i, doc in enumerate(documents):
        doc_id = doc.get("id") or f"__{i}"
        if doc_id in seen:
            continue
        seen.add(doc_id)
        unique_docs.append(
            {
                "id": doc_id,
                "title": doc.get("title"),
                "content": doc.get("content", ""),
                "filepath": doc.get("filepath"),
                "url": doc.get("url"),
            }
        )

    content = getattr(msg, "content", None) or str(msg)
    return {
        "answer": content,
        "role": getattr(msg, "role", "assistant"),
        "documents": unique_docs,
        "thoughts": ctx.get("thoughts") or [],
    }


if __name__ == "__main__":
    import argparse

    # load command line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--query",
        type=str,
        help="Query to use to search subdocuments",
        default="What are the standard office hours?",
    )

    args = parser.parse_args()

    # run chat with subdocuments
    response = chat_with_sub_documents(messages=[{"role": "user", "content": args.query}])