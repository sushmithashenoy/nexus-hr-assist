"""Streamlit UI for Nexus HR Assist — calls the FastAPI backend and shows retrieved documents."""

import os

import requests
import streamlit as st

API_BASE = os.environ.get("HR_API_BASE", "http://127.0.0.1:8000").rstrip("/")


def main() -> None:
    st.set_page_config(page_title="Nexus HR Assist", page_icon="💬", layout="wide")
    st.title("Nexus HR Assist")
    st.caption(f"API: `{API_BASE}` — start the API with: `uvicorn fastapi_app:app --reload`")

    if "messages" not in st.session_state:
        st.session_state.messages = []
    if "last_payload" not in st.session_state:
        st.session_state.last_payload = None

    for m in st.session_state.messages:
        with st.chat_message(m["role"]):
            st.markdown(m["content"])

    query = st.text_area(
        "Your question",
        placeholder='e.g. "What are the standard office hours?"',
        height=100,
    )
    col_ask, col_clear = st.columns([1, 4])
    with col_ask:
        ask_clicked = st.button("Ask HR", type="primary")
    with col_clear:
        if st.button("Clear conversation"):
            st.session_state.messages = []
            st.session_state.last_payload = None
            st.rerun()

    if ask_clicked:
        if not query.strip():
            st.warning("Enter a question.")
            return
        # Send prior turns + this question so intent search and the model see full context.
        thread = [
            *st.session_state.messages,
            {"role": "user", "content": query.strip()},
        ]
        with st.spinner("Searching policies and generating an answer…"):
            try:
                r = requests.post(
                    f"{API_BASE}/api/chat",
                    json={"messages": thread},
                    timeout=120,
                )
                r.raise_for_status()
                data = r.json()
            except requests.RequestException as e:
                st.error(f"Could not reach the API at {API_BASE}. Is uvicorn running? ({e})")
                return

        st.session_state.messages.append({"role": "user", "content": query.strip()})
        st.session_state.messages.append(
            {"role": "assistant", "content": data.get("answer", "")}
        )
        if len(st.session_state.messages) > 5:
            st.session_state.messages.pop(0)
        st.session_state.last_payload = data
        st.rerun()

    payload = st.session_state.last_payload
    if payload:
        thoughts = payload.get("thoughts") or []
        if thoughts:
            with st.expander("Search / intent (debug)", expanded=False):
                for t in thoughts:
                    st.markdown(f"**{t.get('title', '—')}**")
                    st.write(t.get("description", ""))

        docs = payload.get("documents") or []
        st.subheader(f"Documents used for grounding ({len(docs)})")
        if not docs:
            st.info("No document chunks were returned for this query.")
        for i, doc in enumerate(docs, start=1):
            title = doc.get("title") or doc.get("filepath") or doc.get("id") or f"Document {i}"
            with st.expander(f"{i}. {title}", expanded=i <= 3):
                if doc.get("url"):
                    st.markdown(f"[Open link]({doc['url']})")
                if doc.get("filepath"):
                    st.caption(doc["filepath"])
                st.text_area(
                    "Excerpt",
                    value=doc.get("content") or "",
                    height=min(320, 120 + len((doc.get("content") or "")) // 4),
                    key=f"doc_{doc.get('id', i)}",
                    label_visibility="collapsed",
                )


if __name__ == "__main__":
    main()
