from amp.template.backends.utils import AmpComponentsManager, DEFAULT_AMP_VERSION
from django.template import TemplateSyntaxError, Node, Library

register = Library()


class ComponentsNode(Node):
    """
    Template node class used by ``amp.components``.
    """

    def render(self, context):
        amp_components_manager = context.get('_amp_components_manager')
        if not amp_components_manager:
            raise TemplateSyntaxError(
                '{% amp.components %} may only be used with AmpTemplate')

        # Verify that the components manager belongs to this node and is not
        # already used by another one
        if not amp_components_manager.used_by(self):
            raise TemplateSyntaxError(
                '{% amp.components %} may only be called once')
        return context.get('_amp_components_manager').id


class RequireComponentNode(Node):
    """
    Template node class used by ``amp.require_component``.
    """

    def __init__(self, component_name, component_version=DEFAULT_AMP_VERSION):
        self._component_name = component_name
        self._component_version = component_version

    def render(self, context):
        amp_components_manager = context.get('_amp_components_manager')
        if not amp_components_manager:
            raise TemplateSyntaxError(
                '{% amp.require_component %} may only be used with AmpTemplate'
            )
        amp_components_manager.require(self._component_name,
                                       self._component_version)
        return ''


@register.tag('amp.components')
def do_components(parser, token):
    return ComponentsNode()


@register.tag('amp.require_component')
def do_require_component(parser, token):
    args = token.split_contents()
    tag_name = args[0]

    # Get the component name
    try:
        component_name = args[1]
    except ValueError:
        raise TemplateSyntaxError(
            "%r tag first argument needs to be a component name (e.g. amp-sidebar)"
            % tag_name)

    # Get the version
    component_version = args[2] if len(args) == 3 else '"{}"'.format(
        DEFAULT_AMP_VERSION)

    if not (component_name[0] == component_name[-1]
            and component_name[0] in ('"', "'")
            and component_name[0] == component_version[0]
            and component_name[-1] == component_version[-1]):
        raise TemplateSyntaxError("%r tag's arguments should be in quotes" %
                                  tag_name)
    return RequireComponentNode(component_name[1:-1], component_version[1:-1])
