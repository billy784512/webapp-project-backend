from concurrent.futures import ThreadPoolExecutor
from threading import Lock

class ThreadPoolManager:
    _instance = None
    _lock = Lock()

    def __init__(self):
        if ThreadPoolManager._instance is not None:
            raise RuntimeError("Use instance() to access ThreadPoolManager.")
        
        self.read_pool = ThreadPoolExecutor(max_workers=5)
        self.write_pool = ThreadPoolExecutor(max_workers=1)

    @classmethod
    def instance(cls) -> "ThreadPoolManager":
        if cls._instance is None:
            with cls._lock:
                if cls._instance is None:
                    cls._instance = cls()
        return cls._instance
