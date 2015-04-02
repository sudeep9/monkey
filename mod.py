

def add(a,b):
    return a+b


class Person:
    def __init__(self):
        self.name = "A"

    def greet(self):
        print "Hello " + self.name

    @classmethod
    def new(cls):
        return Person()
