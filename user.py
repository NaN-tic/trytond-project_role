from trytond.pool import PoolMeta
from trytond.model import fields


class User(metaclass=PoolMeta):
    __name__ = 'res.user'

    send_own_assignee = fields.Boolean('Send Own Assignee')

    @classmethod
    def __setup__(cls):
        super(User, cls).__setup__()
        if not 'send_own_assignee' in cls._preferences_fields:
            cls._preferences_fields.append('send_own_assignee')
