from app.rag.store import RunbookStore
_store=None
def retrieve(q,k=3):
    global _store
    if _store is None:_store=RunbookStore()
    return _store.search(q,k)
