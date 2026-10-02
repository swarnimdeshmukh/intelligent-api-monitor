from functools import lru_cache
from pydantic_settings import BaseSettings, SettingsConfigDict
class Settings(BaseSettings):
    monitor_interval_seconds:int=5
    request_timeout_seconds:float=5.0
    database_path:str='data/monitoring.db'
    monitor_targets:str='http://127.0.0.1:8000/health,http://127.0.0.1:8000/users,http://127.0.0.1:8000/products,http://127.0.0.1:8000/slow,http://127.0.0.1:8000/error'
    embedding_model:str='all-MiniLM-L6-v2'
    rag_top_k:int=3
    llm_provider:str=''
    llm_model:str=''
    ollama_base_url:str='http://localhost:11434'
    model_config=SettingsConfigDict(env_file='.env',extra='ignore')
    @property
    def targets(self): return [x.strip() for x in self.monitor_targets.split(',') if x.strip()]
@lru_cache
def settings(): return Settings()
