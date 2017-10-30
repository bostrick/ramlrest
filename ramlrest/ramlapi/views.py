
from pyramid.view import view_config
from pyramid.view import view_defaults
from pyramid.response import Response

from .resource import RamlResource
from .ramldumper import RamlDumper

class BaseView(object):

    def __init__(self, context, request):
        self.context = context
        self.request = request


@view_defaults(route_name='raml', context=RamlResource)
class RamlView(BaseView): pass

@view_config(name='')
class DefaultRamlView(RamlView):

    def __call__(self):
        import pdb; pdb.set_trace()
        return Response('hello world')

@view_config(name='debug', renderer='yaml', request_method='GET')
class DebugRamlView(RamlView):

    def __call__(self):
        return RamlDumper.dump(self.context.raml_node)
