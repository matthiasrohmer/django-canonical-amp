from amp.utils import transformer
from django.http.request import validate_host, split_domain_port
import urllib.request, json
from django import http
from urllib.parse import urlparse
from django.conf import settings


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


CACHES_API = 'https://cdn.ampproject.org/caches.json'


def get_cache_domains():
    with urllib.request.urlopen(CACHES_API) as response:
        data = json.loads(response.read().decode())
        cache_domains = []
        for cache in data.get('caches', []):
            # Prepend cache domains with dot to allow all subdomains
            # A little unsecure but less error prone then joining
            # with allowed hosts
            cache_domain = '.{}'.format(cache.get('cacheDomain'))
            cache_domains.append(cache_domain)
        return cache_domains


ALLOWED_ORIGINS = get_cache_domains() + settings.ALLOWED_HOSTS


class AmpCorsMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # return self.get_response(request)
        response = self.process_request(request)
        response = response or self.get_response(request)
        response = self.process_response(request, response)
        return response

    def process_request(self, request):
        request._amp_cors = request.GET.get(
            '__amp_source_origin') or request.META.get('AMP-Same-Origin')
        print(request._amp_cors)
        if request._amp_cors:
            if request.method == 'OPTIONS' and 'HTTP_ACCESS_CONTROL_REQUEST_METHOD' in request.META:
                response = http.HttpResponse()
                response['Content-Length'] = '0'
                return response

    def process_response(self, request, response):
        if not request._amp_cors:
            return response

        origin = urlparse(request.GET['__amp_source_origin']).netloc
        origin = split_domain_port(origin)[0]
        if not validate_host(origin, ALLOWED_ORIGINS):
            return http.HttpResponseForbidden()

        response['Access-Control-Allow-Origin'] = request.META.get(
            'HTTP_ORIGIN', None) or request.GET['__amp_source_origin']
        response['AMP-Access-Control-Allow-Source-Origin'] = request.GET[
            '__amp_source_origin']
        response['Access-Control-Expose-Headers'] = [
            'AMP-Access-Control-Allow-Source-Origin'
        ]
        return response
