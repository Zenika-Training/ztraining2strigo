# coding: utf8

class UNDEFINED_TYPE(str):
    def __bool__(self):
        return False


UNDEFINED = UNDEFINED_TYPE()
