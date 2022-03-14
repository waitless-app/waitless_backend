class ResponseMiddleware(object):
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        is_vendor = False

        try:
            is_vendor = request.META['HTTP_X_SOURCE_WEB']
        except KeyError:
            pass

        request.is_vendor = is_vendor
        response = self.get_response(request)
        return response
