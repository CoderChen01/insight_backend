"""
Encapsulates the basic response data
"""

class BaseResponse:
    """
    the basic response data
    """
    def __init__(self, code, msg, data=None, **kwargs):
        self.code = code
        self.msg = msg
        self.data = data
        if kwargs:
            for key, value in kwargs.items():
                key = str(key)
                self.__dict__[key] = value

    @property
    def result(self):
        return self.__dict__
