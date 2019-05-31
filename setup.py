import os
from setuptools import find_packages, setup

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))

setup(
    name='django-amp',
    version='0.1b',
    packages=find_packages(),
    license='Apache License 2.0',
    description=
    'Template tags and middlewares to make building AMP pages with Django easier.',
    long_description=README,
    url='https://github.com/matthiasrohmer/django-amp',
    author='Matthias Rohmer',
    author_email='rohmer.matthias@anyvent.org',
    install_requires=[
        'Django>=2.1',
    ],
    classifiers=[
        'Environment :: Web Environment',
        'Framework :: Django',
        'Framework :: Django :: 2.1',
        'Framework :: AMP',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: Apache License 2.0',
        'Operating System :: OS Independent',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
        'Topic :: Internet :: WWW/HTTP',
        'Topic :: Internet :: WWW/HTTP :: Dynamic Content',
    ],
)
