import kydb


class EventSignup(kydb.DbObj):
    @kydb.stored
    def signup_type(self):
        """Can be Yes or Maybe"""
        return 'Yes'

    def user(self):
        email = self.key.rsplit('/', 1)[1]
        return self.db['/users/' + email]
