from typing import Callable, Dict, Any
import threading

# 全域快取 room_id 對應的題目資料（如圖像、顏色列表等）
_room_data_cache: Dict[str, Dict[str, Any]] = {}

# 加鎖，避免同時初始化同個 room 資料
_lock = threading.Lock()

def get_or_create_room_data(room_id: str, loader: Callable[[], Dict[str, Any]]) -> Dict[str, Any]:
    """
    傳回該 room_id 的資料（如圖片與顏色），如果第一次呼叫則呼叫 loader 初始化。
    
    :param room_id: 房間 ID（唯一識別碼）
    :param loader: 一個用來生成初始資料的函式（通常會回傳 dict: {image, colors...}）
    :return: 該房間的資料 dict
    """
    if room_id not in _room_data_cache:
        with _lock:
            if room_id not in _room_data_cache:  # double check
                _room_data_cache[room_id] = loader()

    return _room_data_cache[room_id]
