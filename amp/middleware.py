from ctypes import cdll, c_char_p
from os import path
import logging

logger = logging.getLogger(__name__)

class AmpOptimizerMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

        # Set-up the compiled Transformer
        try:
            library_path = path.abspath(
                path.join(path.dirname(__file__), 'vendor/transformer.so'))
            self.transformer = cdll.LoadLibrary(library_path)
            self.transformer.Transform.argtypes = [
                c_char_p,
                c_char_p,
                c_char_p,
            ]
            self.transformer.Transform.restype = c_char_p
        except OSError as e:
            logger.warning('Could not create transformer instance. ' +
                           'AMP pages will not be optimized: {}'.format(e))
            self.transformer = None

        # Set some settings for the transformer
        self.rtv = '011905291911450'

    def __call__(self, request):
        response = self.get_response(request)

        # Check if transformer could have been successfully started
        if not self.transformer:
            return response

        # Verify the response should be optimized
        if not 'text/html' in response.get('Content-Type', ''):
            return response

        content = str(response.content)
        if not '<html amp' in content:
            return response

        response.content = self.transformer.Transform(
            content, request.build_absolute_uri(), self.rtv)
        response['Content-Length'] = len(response.content)

        return response
