from typing import Optional, Any, Dict


class ServiceException(Exception):
    """
    サービス層の基本例外クラス
    """
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)


class DatabaseOperationException(ServiceException):
    """
    データベース操作に関連する例外
    """
    pass


class ResourceNotFoundException(ServiceException):
    """
    リソースが見つからない場合の例外
    """
    pass


class ValidationException(ServiceException):
    """
    入力データのバリデーションに失敗した場合の例外
    """
    pass


class WorkflowException(ServiceException):
    """
    ワークフロー処理に関連する例外
    """
    pass
