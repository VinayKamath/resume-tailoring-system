from pathlib import Path

import chromadb
from chromadb.utils import embedding_functions


class ChromaManager:
    def __init__(self, persist_directory: str = "./chroma_db"):
        self.client = chromadb.PersistentClient(path=persist_directory)

        self.collection = self.client.get_or_create_collection(
            name="resume_knowledge_base"
        )

    def add_documents(self, documents: list[str], source: str):
        """
        Add documents to Chroma.
        """

        ids = [f"{source}_{i}" for i in range(len(documents))]

        metadatas = [
            {"source": source}
            for _ in documents
        ]

        self.collection.add(
            documents=documents,
            ids=ids,
            metadatas=metadatas
        )

    def query(self, query_text: str, n_results: int = 5):
        """
        Retrieve relevant documents.
        """

        results = self.collection.query(
            query_texts=[query_text],
            n_results=n_results
        )

        return results["documents"][0]

    def count(self):
        return self.collection.count()

### Add a helper function

DATA_DIR = Path("data")


def load_text_file(file_path: Path):
    """
    Read lines from txt file.
    """

    if not file_path.exists():
        return []

    with open(file_path, "r", encoding="utf-8") as f:
        lines = [
            line.strip()
            for line in f.readlines()
            if line.strip()
        ]

    return lines

### Add Database Loader

def build_resume_knowledge_base():
    """
    Load all datasets into Chroma.
    """

    chroma = ChromaManager()

    ats_keywords = load_text_file(
        DATA_DIR / "ats_keywords.txt"
    )

    resume_templates = load_text_file(
        DATA_DIR / "resume_templates.txt"
    )

    action_verbs = load_text_file(
        DATA_DIR / "action_verbs.txt"
    )

    chroma.add_documents(
        ats_keywords,
        source="ats_keyword"
    )

    chroma.add_documents(
        resume_templates,
        source="resume_template"
    )

    chroma.add_documents(
        action_verbs,
        source="action_verb"
    )

    return chroma

if __name__ == "__main__":

    chroma = build_resume_knowledge_base()

    print(
        f"Documents stored: {chroma.count()}"
    )

    results = chroma.query(
        "Python data analyst dashboard"
    )

    print("\nRetrieved Documents:\n")

    for doc in results:
        print("-", doc)