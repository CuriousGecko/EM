class ObjectAccessDeniedError(Exception):
    """Ошибка доступа к ресурсу."""

    def __init__(self, message='Доступ запрещен.', status=403):
        self.message = message
        self.status = status
        super().__init__(self.message)
