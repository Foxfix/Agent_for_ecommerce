"""Cuts the policy files into small pieces and stores them in Chroma: python -m knowledge.build"""
import shutil

import config


def pieces(text: str) -> list[str]:
    # One piece per paragraph, with the file's heading in front so each piece makes sense alone.
    lines = text.strip().splitlines()
    title = lines[0].lstrip("# ").strip()
    return [f"{title}: {p.strip()}" for p in "\n".join(lines[1:]).split("\n") if p.strip()]


def build():
    import chromadb

    if config.CHROMA_DIR.exists():
        shutil.rmtree(config.CHROMA_DIR)
    db = chromadb.PersistentClient(path=str(config.CHROMA_DIR))
    col = db.create_collection("policies")
    for f in sorted(config.POLICY_DIR.glob("*.md")):
        docs = pieces(f.read_text())
        col.add(ids=[f"{f.stem}-{i}" for i in range(len(docs))], documents=docs,
                metadatas=[{"file": f.name}] * len(docs))
        print(f"{f.name}: {len(docs)} pieces")
    print("Total:", col.count())


if __name__ == "__main__":
    build()
