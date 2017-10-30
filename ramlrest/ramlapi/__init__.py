
import ramlfications

from .resource import RootRamlResource
from .yaml_renderer import YAMLRenderer


def includeme(config):

    raml_file = config.get_settings()["ramlrest.raml_file"]
    api = ramlfications.parse(raml_file)
    root = RootRamlResource(api)
    root.dump_tree()

    def root_factory(request):
        return root

    config.add_renderer('yaml', YAMLRenderer())
    config.add_route('raml', '/raml/*traverse', factory=root_factory)
