from amp.utils import transformer


class AmpOptimizerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Skip optimizing if opted out via GET-paramter
        if request.GET.get('amp', None):
            return response

        # Verify is a valid HTML response that can be optimized
        if not 'text/html' in response.get('Content-Type', ''):
            return response

        response.content = transformer.transform(
            html=response.content,
            url=request.build_absolute_uri(),
        )
        response['Content-Length'] = len(response.content)

        return response
