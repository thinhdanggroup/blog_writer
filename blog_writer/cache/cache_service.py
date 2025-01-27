import base64
from typing import Any, Optional
from pysondb import db

from blog_writer.config.definitions import ROOT_WORKING_DIR


class CacheService:
    def __init__(self):
        self.cache = db.getDb(f"{ROOT_WORKING_DIR}/cache.json")

    def put(self, key: str, value: Any):
        base64_key = base64.b64encode(key.encode()).decode()
        base64_value = base64.b64encode(value.encode()).decode()
        self.cache.add({"key": base64_key, "value": base64_value})

    def get(self, key: str) -> Optional[Any]:
        base64_key = base64.b64encode(key.encode()).decode()
        val = self.cache.getByQuery({"key": base64_key})
        
        if not val:
            return None
        
        if not val[0].get("value"):
            return None
        
        return base64.b64decode(val[0]["value"]).decode()

global_cache_service = CacheService()