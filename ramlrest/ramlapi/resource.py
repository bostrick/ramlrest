import logging; log = logging.getLogger(__file__)
DEBUG = log.debug; INFO = log.info; WARN = log.warning; ERROR = log.error


class RamlResource(object):

    def __init__(self, raml_node, parent=None, name=''):

        self.__parent__ = parent
        self.__name__ = name

        self.raml_node = raml_node

        def _gen_child_resources():
            for c in raml_node.children:
                #name = c.path[1:].split("/")[0]
                name = c.path.split("/")[-1]
                r = TypedRamlResource(c, parent=self, name=name)
                yield name, r

        self.resource_map = dict(_gen_child_resources())

        #self.resource_map = \
        #    {r.path[1:]:RamlResource(r) for r in raml_node.children}

    def __getitem__(self, key):
        return self.resource_map[key]

    def dump_tree(self):
        print(self)
        for k in sorted(self.resource_map):
            print(k)
            print(self.resource_map[k])

class TypedRamlResource(RamlResource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        # fetch handler based on name
        ERROR("need to fetch handler for %s", self.__name__)

    def __getitem__(self, key):
        import pdb; pdb.set_trace()

class DataRamlResource(RamlResource): pass


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

        for n in api.resources:
            n.parent.children.append(n)
