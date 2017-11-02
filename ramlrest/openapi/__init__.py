
import yaml
from .resource import RootOAIResource


def includeme(config):

    oai_file = config.get_settings()["ramlrest.openapi_file"]
    with open(oai_file) as f:
        api = yaml.load(f.read())
    root = RootOAIResource(api)

    def root_factory(request):
        return root

    config.add_route(
        'openapi', '/openapi/*traverse', factory=root_factory)
