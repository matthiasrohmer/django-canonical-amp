import uuid
from django.template import TemplateSyntaxError, Node, Library

DEFAULT_AMP_VERSION = "0.1"

class AmpComponentsManager(object):
    def __init__(self):
        self.id = str(uuid.uuid4())
        self._components = set()
        self._components_node = None

    def used_by(self, components_node):
        if self._components_node == None or self._components_node == components_node:
            self._components_node = components_node
            return True
        else:
            return False

    def require(self, component, version):
        self._components.add((component, version))

    def render(self, rendered_template):
        script_tags = []
        for component, version in self._components:
            src = 'https://cdn.ampproject.org/v0/{}-{}.js'.format(
                component, version)
            custom_type = 'element' if component is not 'amp-mustache' else 'template'

            script_tags.append(
                '<script custom-{custom_type}="{component}" src="{src}" async></script>'
                .format(custom_type=custom_type, component=component, src=src))
        rendered_template = rendered_template.replace(self.id,
                                                      ''.join(script_tags))
        return rendered_template

    def __repr__(self):
        return '<{}: {} - {}>'.format(
            self.__class__.__name__, self.id, ', '.join(
                [component for component, version in self._components]))
