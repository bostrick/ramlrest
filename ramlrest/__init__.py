from pyramid.config import Configurator
from rht.main.app import Application

def init_zode(config):
    app = Application.get_application()  # force instantiation
    app.initialize_parameters()

def main(global_config, **settings):
    """ This function returns a Pyramid WSGI application.
    """
    config = Configurator(settings=settings)
    init_zode(config)
    config.include('pyramid_jinja2')
    config.include('.ramlapi')
    config.include('.openapi')
    config.add_static_view('static', 'static', cache_max_age=3600)
    config.add_route('home', '/')
    config.scan()
    return config.make_wsgi_app()
