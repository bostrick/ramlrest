import logging; log = logging.getLogger(__file__)
DEBUG = log.debug; INFO = log.info; WARN = log.warning; ERROR = log.error

from pyramid.response import Response
import pyramid.httpexceptions as exc

import ramlfications


class RamlResource(object):

    def __init__(self, node):

        self.node = node
        self.resource_map = {}
        for r in getattr(node, 'resources', []):
            # strip leading "/" from name
            method_map = self.resource_map.setdefault(r.name[1:], {})
            method_map[r.method.lower()] = RamlResource(r)

    def __getitem__(self, key):
        return self.resource_map[key]

class RootRamlResource(RamlResource):

    def __init__(self, api):
        DEBUG("init root resource %s", api)
        super(RootRamlResource, self).__init__(api)
        self.api = api

def default_view(context, request):

    #import pdb; pdb.set_trace()

    if isinstance(context, RootRamlResource):
        return Response('hello root:%s' % context)

    r = context.get(request.method.lower())
    if not r:
        raise exc.HTTPBadRequest("method %s not allowed." % request.method)

    return Response('hello world:%s' % r)

def includeme(config):
    raml_file = config.get_settings()["ramlrest.raml_file"]
    api = ramlfications.parse(raml_file)
    root = RootRamlResource(api)

    def root_factory(request):
        return root

    config.add_route('raml', '/raml/*traverse', factory=root_factory)
    config.add_view(default_view, route_name='raml')
