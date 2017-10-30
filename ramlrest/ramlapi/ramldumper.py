import logging; log = logging.getLogger(__file__)
DEBUG = log.debug; INFO = log.info; WARN = log.warning; ERROR = log.error

from attr import asdict as attr_asdict
import ramlfications

class RamlDumper(object):

    klass = None             # subclass responsibility
    REGISTRY=[]

    omit_list = "config root parent".split()
    non_iter_iterables= (str, dict)

    @classmethod
    def register(cls, subclass):
        cls.REGISTRY.append((subclass.klass, subclass))
        return cls

    @classmethod
    def get_dumper_for_object(cls, obj):
        for match_class, klass in cls.REGISTRY:
            if isinstance(obj, match_class):
                return klass(obj)

    @classmethod
    def dump(cls, object):
        d = cls.get_dumper_for_object(object)
        return d.asdict() if d else object

    def __init__(self, context):
        self.context = context

    def asdict(self):

        def _gen_values(adict):

            #import pdb; pdb.set_trace()
            for key, value in adict.items():

                if (not value) or (key in self.omit_list):
                    continue

                yield "_type", self.context.__class__.__name__

                if key == 'config':
                    import pdb; pdb.set_trace()
                # note this forces all iterables to a list...
                nii = self.non_iter_iterables
                if hasattr(value, "__iter__") and not isinstance(value, nii):
                    yield key, [ self.dump(v) for v in value ]
                else:
                    yield key, self.dump(value)

        d = attr_asdict(self.context, recurse=False)
        return dict(_gen_values(d))

@RamlDumper.register
class RamlRootNodeDumper(RamlDumper):

    klass = ramlfications.raml.RootNode
    #omit_list = RamlDumper.omit_list[:]
    #omit_list.remove('config')

@RamlDumper.register
class RamlBaseNodeDumper(RamlDumper):

   klass = ramlfications.raml.BaseNode
   omit_list = RamlDumper.omit_list + ['resources']

@RamlDumper.register
class RamlParameterDumper(RamlDumper):

     klass = ramlfications.parameters.BaseParameter

@RamlDumper.register
class RamlBodyDumper(RamlDumper):

     klass = ramlfications.parameters.Body

@RamlDumper.register
class RamlResponseDumper(RamlDumper):

     klass = ramlfications.parameters.Response
