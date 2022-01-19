

class PollsBaseException(Exception):
    pass


class NotFoundError(PollsBaseException):
    pass


class NotUniqueError(PollsBaseException):
    pass
