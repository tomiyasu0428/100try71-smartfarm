import json
from typing import Any, List, Dict, Optional, TypeVar, Generic, Type

T = TypeVar('T')


def parse_json_string(json_str: Optional[str]) -> Any:
    """
    JSON文字列をPythonオブジェクトに変換する
    
    Args:
        json_str: JSON文字列
        
    Returns:
        変換されたPythonオブジェクト、またはNone（入力がNoneまたは空文字列の場合）
    """
    if not json_str:
        return None
    try:
        return json.loads(json_str)
    except json.JSONDecodeError:
        return None


def to_json_string(obj: Any) -> str:
    """
    PythonオブジェクトをJSON文字列に変換する
    
    Args:
        obj: 変換するPythonオブジェクト
        
    Returns:
        JSON文字列
    """
    return json.dumps(obj)
