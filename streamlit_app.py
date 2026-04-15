"""Streamlit UI for Nexus HR Assist — calls the FastAPI backend and shows retrieved documents."""

import os

import requests
import streamlit as st

API_BASE = os.environ.get("HR_API_BASE", "http://127.0.0.1:8000").rstrip("/")


def main() -> None:
    st.set_page_config(page_title="Nexus HR Assist", page_icon="💬", layout="wide")
    st.title("Nexus HR Assist")
    st.caption(f"API: `{API_BASE}` — start the API with: `uvicorn fastapi_app:app --reload`")

    query = st.text_area(
        "Your question",
        placeholder='e.g. "What are the standard office hours?"',
        height=100,
    )
    if st.button("Ask HR", type="primary"):
        if not query.strip():
            st.warning("Enter a question.")
            return
        with st.spinner("Searching policies and generating an answer…"):
            try:
                r = requests.post(
                    f"{API_BASE}/api/chat",
                    json={"query": query.strip()},
                    timeout=120,
                )
                r.raise_for_status()
                data = r.json()
            except requests.RequestException as e:
                st.error(f"Could not reach the API at {API_BASE}. Is uvicorn running? ({e})")
                return

        st.subheader("Answer")
        st.markdown(data.get("answer", ""))

        thoughts = data.get("thoughts") or []
        if thoughts:
            with st.expander("Search / intent (debug)", expanded=False):
                for t in thoughts:
                    st.markdown(f"**{t.get('title', '—')}**")
                    st.write(t.get("description", ""))

        docs = data.get("documents") or []
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
