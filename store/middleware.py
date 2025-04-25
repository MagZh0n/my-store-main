class PrintUserMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
 
    def __call__(self, request):
        response = self.get_response(request)
        print(f"\nMiddleware Check - User: {request.user}, Auth: {request.user.is_authenticated}")
        return response