import logging; log = logging.getLogger(__file__)
DEBUG = log.debug; INFO = log.info; WARN = log.warning; ERROR = log.error

import re

from zode.zca import zca_manager as zca
from zode.doc.interfaces import IDocumentStoreFactory

class OAIResource(object):

    """

        TODO:
            - better handle path templating
    """

    operation_object_names = """
        get put post delete options head patch trace
    """.split()

    named_child_class = None
    paramaterized_child_class = None

    def __init__(self, oai_node, parent=None, name=''):

        self.__parent__ = parent
        self.__name__ = name

        self.oai_node = oai_node

    def __getitem__(self, key):

        cmap = self.oai_children

        # first look for explicit match
        n = cmap.get(key)
        if n and (not n.get('_has_path_param')):
            klass = self.named_child_class or NamedOAIResource
            return klass(n, parent=self, name=key)

        # now query all path param children (does spec allow more than one?)
        # how to improve efficiency? hopefully paramaterized children do
        # not have many sibilings...
        for k, n in cmap.items():

            if not n.get('_has_path_param'):
                continue

            try:
                klass = self.paramaterized_child_class \
                            or ObjectOAIResource
                r = klass(n, parent=self, name=key)
                return r
            except KeyError:
                continue

        # no one recognized the name...
        raise KeyError(key)

    @property
    def oai_children(self):
        return self.oai_node.get('_children', {})

    @property
    def methods(self):
        n = self.oai_node
        return {k:n[k] for k in self.operation_object_names if k in n}

    @property
    def parameters(self):

        """ return a three deep dict of parameters, keyed by

                - request method (or 'global')
                - parameter['in']
                - parameter['name']
        """

        p_map = {}

        for p in self.oai_node.get("parameters", []):
            m_map = p_map.setdefault('global', {})
            m_map.setdefault(p['in'], {})[p["name"]] = p

        for method_name, method in self.methods.items():
            for p in method.get("parameters", []):
                m_map = p_map.setdefault(method_name, {})
                m_map.setdefault(p['in'], {})[p["name"]] = p

        return p_map

    def as_dict(self):
        """ dump for diagnostics """
        return {
            'name': self.__name__,
            'paramaters': self.parameters,
            'oai_node': self.oai_node,
        }


class NamedOAIResource(OAIResource):

    def __init__(self, *args, **kwargs):

        super().__init__(*args, **kwargs)

        # fetch handler based on name
        dsf = zca.get_utility(IDocumentStoreFactory)
        self.store = dsf.new_from_spec(self.__name__)
        INFO("found store %s for %s", self.store, self.__name__)

    #def __getitem__(self, key):
    #    doc = self.store.get(key)
    #    if doc:
    #        return

    def as_dict(self):
        d = super().as_dict()
        d["store"] = str(self.store)
        return d

class ParameterizedOAIResource(OAIResource):

    pass

class ObjectOAIResource(OAIResource):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        if not self.item:
            raise KeyError(self.__name__)

    @property
    def store(self):
        return self.__parent__.store

    @property
    def item(self):
        return self.store.get(self.__name__)


class RootOAIResource(OAIResource):

    is_param_match = re.compile("\{.+\}").match

    def __init__(self, api):

        self.api = self.oai_node = api
        self._build_path_children()
        super(RootOAIResource, self).__init__(api)

    def _build_path_children(self):


        pmap = self.api["paths"]
        for path in sorted(pmap):
            parent, _, child = path.rpartition("/")
            if not child:
                continue
            pnode = pmap[parent] if parent else self.api
            pnode.setdefault("_children", {})[child] = pmap[path]

            # label parameterized nodes
            pmap[path]['_has_path_param'] = bool(self.is_param_match(child))
