from ctypes import cdll, c_char_p
from os import path
import platform
import urllib.request, json
from django.conf import settings

METADATA_API = 'https://cdn.ampproject.org/rtv/metadata'


def get_metadata():
    with urllib.request.urlopen(METADATA_API) as response:
        data = json.loads(response.read().decode())
        return data


RUNTIME_VERSION = get_metadata().get('ampRuntimeVersion')

SHARED_LIBRARIES = {
    'linux': 'lib/transformer-linux-amd64.so',
    'darwin': 'lib/transformer-darwin-10.6-amd64.dylib',
}


class Transformer(object):
    """
    Creates an instance of the Go transformer originally used by the amppackager
    which allows to perform SSR for AMP pages from Python
    """

    def __init__(self):
        try:
            platform_system = platform.system()
            library_path = path.abspath(
                path.join(
                    path.dirname(__file__),
                    SHARED_LIBRARIES.get(platform.system().lower()),
                ))
            self.transformer = cdll.LoadLibrary(library_path)
            self.transformer.Transform.argtypes = [
                c_char_p,
                c_char_p,
                c_char_p,
            ]
            self.transformer.Transform.restype = c_char_p
        except Exception as e:
            raise RuntimeError(
                ("Couldn't create an AMP transformer for your environment. "
                 "Possibly your architecture isn't supported."
                 "Currently supported archs are: linux/amd64 and darwin/amd64."
                 "You are running: " + platform.system())) from e

    def transform(self, html='', url=None, rtv=RUNTIME_VERSION):
        # Try to convert a possible byte string to a normal string
        try:
            html = html.decode('utf-8')
        except AttributeError:
            pass

        # Do not rewrite URLs in DEBUG mode or if AMP_REWRITE_URLS is False
        if settings.DEBUG or not getattr(settings, 'AMP_REWRITE_URLS',
                                         not settings.DEBUG):
            url = None

        # Only optimize AMP pages
        if not '<html amp' in html and not '<html ⚡' in html:
            return html

        return self.transformer.Transform(bytes(html, 'utf-8'),
                                          bytes(url or '', 'utf-8'),
                                          bytes(rtv, 'utf-8'))


# Export transformer to be easily importable
transformer = Transformer()
