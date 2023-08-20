from json import JSONEncoder


# subclass JSONEncoder
class ObjectEncoder(JSONEncoder):
    def default(self, o):
        return o.__dict__
