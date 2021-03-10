# coding: utf8

class UNDEFINED_TYPE:
    def __bool__(self):
        return False


UNDEFINED = UNDEFINED_TYPE()
