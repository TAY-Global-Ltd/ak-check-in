import base64
import kydb

COLOR_BLACK = 4278190080
COLOR_WHITE = 4294967295


class AKUser(kydb.DbObj):
    @kydb.stored
    def name(self) -> str:
        return ''

    @kydb.stored
    def alias(self) -> str:
        return ''

    @kydb.stored
    def display_style(self) -> str:
        return {
            'background-color': COLOR_WHITE,
            'color': COLOR_BLACK
        }

    def email(self) -> str:
        return self.key.rsplit('/', 1)[1]

    @kydb.stored
    def is_full_member(self) -> bool:
        return False

    @kydb.stored
    def is_outdoor_member(self) -> bool:
        return False

    def is_member(self) -> bool:
        return self.is_full_member() or self.is_outdoor_member()

    @staticmethod
    def jwt_decode(token):
        body = token.split('.')[1]
        remain = len(body) % 4
        if remain == 2:
            body += '=='
        elif remain == 3:
            body += '='

        return base64.b64decode(body)

    @staticmethod
    def get_user_path(user_id):
        return f'/users/{user_id}'
