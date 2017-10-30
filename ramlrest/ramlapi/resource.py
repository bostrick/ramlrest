import logging; log = logging.getLogger(__file__)
DEBUG = log.debug; INFO = log.info; WARN = log.warning; ERROR = log.error


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
        list(map(_init_children, api.resources))
        #r_map = {n.path:_init_children(n) for n in api.resources}
        for n in api.resources:
            n.parent.children.append(n)
