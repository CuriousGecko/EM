from enum import Enum


class Action(str, Enum):
    READ = 'read'
    CREATE = 'create'
    UPDATE = 'update'
    DELETE = 'delete'

    def __str__(self):
        return self.value
