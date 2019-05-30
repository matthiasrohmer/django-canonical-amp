import os
import sys
import subprocess
import shutil
from setuptools import find_packages, setup
from setuptools.command.install import install

with open(os.path.join(os.path.dirname(__file__), 'README.md')) as readme:
    README = readme.read()

# Allow setup.py to be run from any path
os.chdir(os.path.normpath(os.path.join(os.path.abspath(__file__), os.pardir)))


# Custom install command class to support building a shared library from Go
class TransformerInstall(install):
    def check_version(self):
        cmd = ['go', 'version']
        try:
            subprocess.check_call(cmd, stderr=subprocess.STDOUT)
        except subprocess.CalledProcessError as e:
            raise Exception(
                'This package relies on golang 1.5 or newer being installed.')

    def prepare(self):
        # Clean build directory possibly created in previous runs
        if os.path.exists('.build'):
            shutil.rmtree('.build')

        # Setup virtual GOPATH
        os.makedirs(os.path.join(os.getcwd(), '.build'))
        os.environ['GOPATH'] = os.path.join(os.getcwd(), '.build')

        # Download dependencies
        print('Fetching transformer dependencies ...')
        return subprocess.call('go get'.split())

    def build(self):
        print('Building transformer ...')
        cmd = 'go build -a -o amp/vendor/transformer.so -buildmode=c-shared transformer.go'
        return subprocess.check_call(cmd.split())

    def run(self):
        self.check_version()
        try:
            self.prepare()
            self.build()
        except Exception as e:
            sys.stderr.write(
                'Could not build transformer needed for django-amp: ' +
                '{}'.format(e))
            raise
        self.do_egg_install()


setup(
    name='django-amp',
    version='0.1',
    cmdclass={'install': TransformerInstall},
    packages=find_packages(),
    include_package_data=True,
    license='Apache License 2.0',
    description=
    'Template tags and middlewares to make building AMP pages with Django easier.',
    long_description=README,
    url='https://github.com/matthiasrohmer/django-amp',
    author='Matthias Rohmer',
    author_email='rohmer.matthias@anyvent.org',
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
