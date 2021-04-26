from django.utils.deprecation import MiddlewareMixin

class GlobalRequestMiddleware(MiddlewareMixin):
    __instance__ = None
    
    #singleton
    def __new__(cls, *args, **kwargs):
        if not cls.__instance__:
            cls.__instance__ = object.__new__(cls)
        return cls.__instance__
    
    def process_request(self, request):
        GlobalRequestMiddleware.__instance__ = request

    @classmethod
    def getRequest(cls):
        return cls.__instance__
