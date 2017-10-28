import logging; log = logging.getLogger(__file__)
DEBUG = log.debug; INFO = log.info; WARN = log.warning; ERROR = log.error

import yaml

#from pyramid.response import Response
#import pyramid.httpexceptions as exc

import ramlfications

from .ramldumper import RamlDumper


class RamlResource(object):

    def __init__(self, raml_node):

        self.raml_node = raml_node
        self.resource_map = \
            {r.path:RamlResource(r) for r in raml_node.children}

    def __getitem__(self, key):
        return self.resource_map['/'+key]

    def dump_tree(self):
        print(self)
        for k in sorted(self.resource_map):
            print(k)
            print(self.resource_map[k])

class RootRamlResource(RamlResource):

    def __init__(self, api):
        self.api = api
        self._build_resource_children(api)
        super(RootRamlResource, self).__init__(api)

    def _build_resource_children(self, api):

        def _init_children(n):
            if not n.parent:
                n.parent = api
            n.children = []
            return n

        api.children = []
        r_map = {n.path:_init_children(n) for n in api.resources}
        for n in api.resources:
            n.parent.children.append(n)

def default_view(context, request):
    return RamlDumper.dump(context.raml_node)

class YAMLRenderer(object):

    def __call__(self, info):
        def _render(value, system):
            request = system.get('request')
            if request is not None:
                response = request.response
                ct = response.content_type
                if ct == response.default_content_type:
                    #response.content_type = 'application/yaml'
                    response.content_type = 'text/plain'
            return yaml.dump(value, default_flow_style=False)

        return _render


def includeme(config):
    raml_file = config.get_settings()["ramlrest.raml_file"]
    api = ramlfications.parse(raml_file)
    root = RootRamlResource(api)
    root.dump_tree()

    def root_factory(request):
        return root

    config.add_renderer('yaml', YAMLRenderer())

    config.add_route('raml', '/raml/*traverse', factory=root_factory)
    config.add_view(default_view, route_name='raml', renderer='yaml')
