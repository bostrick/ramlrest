from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.response import Response
from pyramid.renderers import render_to_response

from .resource import OAIResource
from .resource import NamedOAIResource
from .resource import ObjectOAIResource


class BaseView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request


@view_defaults(route_name='openapi', context=OAIResource)
class OAIView(BaseView):

    def __call__(self):

        m = self.request.method.lower()
        f = getattr(self, m, None)
        if f:
            return f()


@view_config(name='')
class DefaultOAIView(OAIView):

    def get(self):
        return Response('hello from %s'%self.context.__name__)

@view_config(name='', context=NamedOAIResource, renderer='json')
class NamedOAIView(OAIView):

    def get(self):
        s = self.context.store
        return list(s.scan())

class ObjectOAIView(OAIView):

    @property
    def type_name(self):
        return self.context.__parent__.__name__

    @property
    def item(self):
        return self.context.item

@view_config(name='', context=ObjectOAIResource,
             accept='application/json', renderer='json')
class JSONObjectOAIView(ObjectOAIView):

    def get(self):
        return self.item

@view_config(name='', accept='text/html', context=ObjectOAIResource)
class TemplateObjectOAIView(ObjectOAIView):

    @property
    def template_name(self):
        return "templates/%s.jinja2" % self.type_name

    def get(self):
        return render_to_response(
            self.template_name,
            {'item': self.item, },
            request=self.request
        )

@view_config(name='debug', renderer='json', request_method='GET')
class DebugOAIView(OAIView):

    def __call__(self):
        return self.context.as_dict()

@view_config(name='schema', renderer='json', context=OAIResource)
class SchemaOAIView(OAIView):

    def get(self):
        return self.context.store.doc_type.schema
