from datetime import datetime, timedelta
from typing import Dict, Any, Optional

class ScalingCache:
    """In-memory calculation cache preventing redundant execution overhead."""
    def __init__(self, ttl_seconds: int = 300):
        # Initialized with an empty dictionary to store cached results
        self.cache: Dict[str, Any] = {}
        self.ttl = ttl_seconds

    def get(self, recipe_id: str, target_servings: int) -> Optional[Dict[str, Any]]:
        key = f"{recipe_id}:{target_servings}"
        entry = self.cache.get(key)
        
        # Validate entry and check expiration time (Time-To-Live)
        if entry and datetime.now() < entry["expires"]:
            return entry["result"]
        return None

    def set(self, recipe_id: str, target_servings: int, result: Dict[str, Any]) -> None:
        key = f"{recipe_id}:{target_servings}"
        self.cache[key] = {
            "result": result,
            "expires": datetime.now() + timedelta(seconds=self.ttl)
        }