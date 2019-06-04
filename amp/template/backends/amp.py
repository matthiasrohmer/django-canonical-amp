from amp.templatetags.amp import ComponentsNode
from django.template import TemplateDoesNotExist
from django.template.context import make_context
from django.template.backends.django import DjangoTemplates, Template, reraise
from amp.template.backends.utils import AmpComponentsManager


class AmpTemplates(DjangoTemplates):
    def from_string(self, template_code):
        return AmpTemplate(self.engine.from_string(template_code), self)

    def get_template(self, template_name):
        try:
            return AmpTemplate(self.engine.get_template(template_name), self)
        except TemplateDoesNotExist as exc:
            reraise(exc, self)


class AmpTemplate(Template):
    def render(self, context=None, request=None):
        amp_components_manager = AmpComponentsManager()
        context['_amp_components_manager'] = amp_components_manager
        context = make_context(context,
                               request,
                               autoescape=self.backend.engine.autoescape)
        try:
            rendered_template = self.template.render(context)
        except TemplateDoesNotExist as exc:
            reraise(exc, self.backend)
        return amp_components_manager.render(rendered_template)
