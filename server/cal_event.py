import kydb


class EventSignup(kydb.DbObj):
    @kydb.stored
    def signup_type(self):
        """Can be Yes or Maybe"""
        return 'Yes'

    @kydb.stored
    def participant_id(self) -> id:
        """The ID of the participant -1 means the main participant
        And positive int would be the index of the participant in the list of participants
        """
        return -1

    def user(self):
        email = self.key.rsplit('/', 1)[1]
        return self.db['/users/' + email]
