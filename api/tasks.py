from typing import Dict, List, Optional, Any

# 暫時的 stub（不依賴 backend_tasks），讓後端可以啟動
def trigger_youtube_ingest(channel_ids: Optional[List[str]] = None) -> Dict[str, Any]:
    # TODO: 未來改成丟 Celery 任務，現在先回傳排隊成功
    return {
        "status": "queued",
        "channels": channel_ids or [],
        "note": "stub implementation (backend_tasks.py has a syntax error to fix)"
    }
