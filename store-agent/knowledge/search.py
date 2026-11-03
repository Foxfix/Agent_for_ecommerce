"""The policy search tool the agent uses."""
import re

from strands import tool

import config
from knowledge.build import pieces

WORD = re.compile(r"[a-z0-9]+")


def _chroma(question: str) -> list[dict]:
    import chromadb
    col = chromadb.PersistentClient(path=str(config.CHROMA_DIR)).get_collection("policies")
    hits = col.query(query_texts=[question], n_results=4)
    return [{"file": m["file"], "text": d} for d, m in zip(hits["documents"][0], hits["metadatas"][0])]


def _keyword(question: str) -> list[dict]:
    # A light search for the cloud: score each piece by shared words.
    q = {w.rstrip("s") for w in WORD.findall(question.lower()) if len(w) > 2}
    scored = []
    for f in sorted(config.POLICY_DIR.glob("*.md")):
        for text in pieces(f.read_text()):
            words = {w.rstrip("s") for w in WORD.findall(text.lower())}
            scored.append((len(q & words), f.name, text))
    scored.sort(key=lambda s: -s[0])
    return [{"file": name, "text": text} for score, name, text in scored[:4] if score]


@tool
def search_policies(question: str) -> list[dict]:
    """Search the store's policies (shipping, returns, sizes). Returns the most relevant passages."""
    return _keyword(question) if config.KNOWLEDGE == "keyword" else _chroma(question)


if __name__ == "__main__":
    import sys
    for hit in search_policies(" ".join(sys.argv[1:]) or "Can I return worn shoes?"):
        print(f'[{hit["file"]}] {hit["text"]}')
