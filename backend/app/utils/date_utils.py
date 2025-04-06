from typing import Optional
from datetime import datetime, date


def convert_iso_to_date(iso_date_str: Optional[str]) -> Optional[date]:
    """
    ISO形式の日付文字列をdate型に変換する
    
    Args:
        iso_date_str: ISO形式の日付文字列（例: "2023-01-01T00:00:00Z"）
        
    Returns:
        date型のオブジェクト、またはNone（入力がNoneの場合）
    """
    if not iso_date_str:
        return None
    return datetime.fromisoformat(iso_date_str.replace("Z", "+00:00")).date()


def convert_date_to_iso(date_obj: Optional[date]) -> Optional[str]:
    """
    date型をISO形式の文字列に変換する
    
    Args:
        date_obj: date型のオブジェクト
        
    Returns:
        ISO形式の日付文字列、またはNone（入力がNoneの場合）
    """
    if not date_obj:
        return None
    return date_obj.isoformat()
