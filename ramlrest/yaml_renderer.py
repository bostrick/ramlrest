
import yaml

import logging; log = logging.getLogger(__file__)
DEBUG = log.debug; INFO = log.info; WARN = log.warning; ERROR = log.error


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
