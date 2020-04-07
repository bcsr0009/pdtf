import logging

class logwrap(object):

    def __init__(self, f):
        self.f = f

    def __call__(self, *args, **kwargs):
        logging.debug( "Entering into " + self.f.__name__ )
        response = self.f(*args, **kwargs)
        logging.debug("Exiting from " +  self.f.__name__)
        return response