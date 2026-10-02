from pathlib import Path
import faiss
from sentence_transformers import SentenceTransformer
from app.config import settings
class RunbookStore:
    def __init__(self): self.model=SentenceTransformer(settings().embedding_model); self.docs=[]; self.index=None
    def load(self):
        self.docs=[{'source':p.name,'text':p.read_text(encoding='utf-8')} for p in sorted(Path('data/runbooks').glob('*.md'))]
        if not self.docs:return
        e=self.model.encode([d['text'] for d in self.docs],normalize_embeddings=True,convert_to_numpy=True).astype('float32'); self.index=faiss.IndexFlatIP(e.shape[1]); self.index.add(e)
    def search(self,q,k=3):
        if self.index is None:self.load()
        if self.index is None:return []
        v=self.model.encode([q],normalize_embeddings=True,convert_to_numpy=True).astype('float32'); scores,ids=self.index.search(v,min(k,len(self.docs)))
        return [{**self.docs[i],'score':float(s)} for s,i in zip(scores[0],ids[0]) if i>=0]
