from pydantic import BaseModel

# 通用基底：允許任意欄位，避免驗證擋住先啟動
class _Base(BaseModel):
    model_config = {"extra": "allow"}  # pydantic v2

# PEP 562：當 from .schemas import X 時，若 X 不存在，動態建立
def __getattr__(name: str):
    return type(name, (_Base,), {})
