[![PyPI version](https://badge.fury.io/py/django-canonical-amp.svg)](https://badge.fury.io/py/django-canonical-amp)

# django-canonical-amp

A small set of tools meant to make building canonical [AMP](https://amp.dev) pages with [Django](https://www.djangoproject.com/) a little easier.

## Installation

To enable the functionality of this package you need to add it to various keys of your project settings (settings.py per default) just as with other Django apps.

#### INSTALLED_APPS
django-canonical-amp needs to be added to your installed apps.

```python
INSTALLED_APPS = [
  # ...
  'amp',
]
```

#### TEMPLATES
Additionally you need to update your template settings to use the django-canonical-amp backend which is just a wrapper around Django's default backend.


```python
TEMPLATES = [
  {
    'BACKEND': 'amp.template.backends.amp.AmpTemplates',
    # ...
  },
]
```

#### MIDDLEWARE
This step is optional but if you want to serve [server-side-rendered AMP](https://github.com/ampproject/amphtml/blob/master/spec/amp-cache-modifications.md) straight from your Django app you can add the transformer middleware to your stack.

**Important:** this is experimental. The transformations happen by using a shared library built from the Go implementation of the [amppackager](https://github.com/ampproject/amppackager/tree/releases/transformer). This package ships with compiled versions for *linux/amd64* and *darwin/amd64* operating systems.

If you want to use this middleware you also need to make sure your production system is able to perform requests to https://cdn.ampproject.org/rtv/metadata for the transformer to be able to fetch the current runtime version.

```python
MIDDLEWARE = [
  # ...
  'amp.middleware.AmpOptimizerMiddleware',
]
```

This middleware needs to execute before Django's `django.middleware.gzip.GZipMiddleware` for the transformer to be able to alter the response.

If you make use of this middleware you can additionally set `AMP_REWRITE_URLS` in your settings to `False`. By doing so you instruct the transformer to leave your URLs alone and don't rewrite them to a AMP cache URL - this comes with pros and cons: delivery times might be better from the cache though there's no guarantee your content (and assets) are already available from the cache. This settings defaults to `not DEBUG` to don't rewrite URLs for all non-production environments.

AMP components relying on API endpoints served by your application need them to be served according to [AMP's CORS specification](https://amp.dev/documentation/guides-and-tutorials/learn/amp-caches-and-cors/amp-cors-requests). django-canonical-amp ships with another middleware that adds the required headers. For it to work make sure your server is able to access https://cdn.ampproject.org/caches.json. Then add the middleware to your stack:

```python
MIDDLEWARE = [
  # ...
  'amp.middleware.AmpCorsMiddleware',
]
```

## Usage
The basic functionality of the package are two template tags that are available after installation. They make it able to dynamically define used [AMP components](https://amp.dev/documentation/components/). For them to and up in the `<head>` of your HTML make sure you add the `{% amp.components %}` tag like so:

```html
{% load amp %}

<!DOCTYPE html>
<html ⚡ lang="de">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width,minimum-scale=1">
    <meta name="description" content="{{ description }}">

    <link rel="preload" as="script" href="https://cdn.ampproject.org/v0.js">
    <script async src="https://cdn.ampproject.org/v0.js"></script>

    {% amp.components %}
    <!-- This will expand to a list of <script> tags:
    <script async custom-element="amp-..." src="https://cdn.ampproject.org/v0/amp-...-0.1.js"></script>
    -->

    <style amp-custom>
    {% block style %}
    {% endblock %}
    </style>
```

Somewhere else in your templates you can then define dependencies by calling `{% amp.require_component "<component>" "<version>" %}` like in the following example:

```html
{% if youtube_id %}
{% amp.require_component "amp-youtube" %}
<amp-youtube
    data-videoid="{{ youtube_id }}"
    layout="responsive"
    width="480" height="270"></amp-youtube>
{% endif %}
```

 If `youtube_id` evaluates to `False` in the above example the `amp-youtube` extension would not be injected to your page and it would stay AMP valid.

The version can be omitted. It will then default to 0.1.
