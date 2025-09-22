import json


class ValidationError(Exception):
    """Исключение для ошибок валидации."""

    def __init__(self, message, status=400):
        super().__init__(message)
        self.message = message
        self.status = status


class JsonParseError(ValidationError):
    """Специализированное исключение для ошибок парсинга JSON."""
    pass


def parse_json_body(request):
    """
    Парсит JSON body запроса и возвращает dict.
    В случае ошибки выбрасывает JsonParseError.
    """
    if request.content_type != 'application/json':
        raise JsonParseError(
            'Требуется Content-Type: application/json',
            status=415
        )

    try:
        return json.loads(request.body.decode('utf-8'))
    except json.JSONDecodeError:
        raise JsonParseError('Неверный JSON формат', status=400)
    except UnicodeDecodeError:
        raise JsonParseError('Неверная кодировка данных', status=400)
