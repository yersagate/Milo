# milo_rag.py
from pathlib import Path
import pypdf

class MiloRAG:
    def __init__(self, docs_dir="./docs"):
        self.docs_dir = Path(docs_dir)
        self.documents = {}
        self.index_folder()

    def index_folder(self):
        """Indexes all TXT, MD, and PDF files in the specified directory."""
        if not self.docs_dir.exists():
            self.docs_dir.mkdir(exist_ok=True, parents=True)
            return

        self.documents.clear()
        for file_path in self.docs_dir.iterdir():
            if file_path.is_file():
                ext = file_path.suffix.lower()
                text = ""
                try:
                    if ext in [".txt", ".md"]:
                        text = file_path.read_text(encoding="utf-8")
                    elif ext == ".pdf":
                        reader = pypdf.PdfReader(str(file_path))
                        text = "\n".join([page.extract_text() for page in reader.pages if page.extract_text()])

                    if text:
                        self.documents[file_path.name] = text
                except Exception as e:
                    print(f"Error indexing {file_path.name}: {e}")

    def search(self, query, top_k=2):
        """Searches indexed documents for relevant content based on keyword matching."""
        query_words = set(query.lower().split())
        scored = []
        for name, content in self.documents.items():
            content_lower = content.lower()
            score = sum(content_lower.count(word) for word in query_words)
            if score > 0:
                scored.append((score, name, content))

        scored.sort(key=lambda x: x[0], reverse=True)
        return scored[:top_k]
