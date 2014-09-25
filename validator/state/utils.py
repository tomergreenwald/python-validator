import copy
import types
import ast

TOP_MAGIC_NAME = "MAKE_THIS_VAR_AS_TOP"

def tmp_f():
    pass
tmp_int = 5
class tmp_T(object):
    def f(self):
        pass

class TopFunction(object):
    index = -1
    @staticmethod
    def get(num_args):
        TopFunction.index += 1
        return ast.parse('\ndef func_%s_%d(%s):\n    return %s_%d\n' %(TOP_MAGIC_NAME, TopFunction.index, ', '.join(['arg%d' %j for j in xrange(num_args)]), TOP_MAGIC_NAME, TopFunction.index)).body[0]

class IntFunction(object):
    index = -1
    @staticmethod
    def get(num_args):
        IntFunction.index += 1
        return ast.parse('\ndef func_%s_%d(%s):\n    return 0\n' %('MAKE_THIS_AS_INT', IntFunction.index, ', '.join(['arg%d' %j for j in xrange(num_args)]))).body[0]
        
PRIMITIVES = set([eval('types.%s' %x) for x in dir(types) if x.endswith('Type')])
CALLABLES = set(map(type, [tmp_f, tmp_int.__add__, tmp_T().f]))

def is_primitive(obj):
    # sometime copy fails (for example when we create an empty class and look at its __init__ method
    # maybe the assumption of primitive in this case is not correct
    """
    try:
        clone = copy.deepcopy(obj)
    except:
        return True
    """
    
    try:
        obj.fdsfsdfdsfdsfdsfdsfdsfds = 5
        del obj.fdsfsdfdsfdsfdsfdsfdsfds
        return False
    except:
        return True
        
def is_callable(obj):
    """
    check if obj is a function
    """
    return type(obj) in CALLABLES
        
def var_to_father(var_name):
    """
    converts var of form: f#g#h#x.a.b to be f#g#h#x.a
    """
    last_sep = var_name.rfind('#') + 1
    scope = var_name[:last_sep]
    base_name = var_name[last_sep:]
    last_dot = base_name.rfind('.')
    if last_dot < 0:
        return ''
    father = base_name[:last_dot]
    return scope + father

def var_to_basename(var_name):
    """
    converts var of form: f#g#h#x.a.b to be b
    and var of the form f#g#h#x to be unchanged
    """
    last_dot = var_name.rfind('.')
    
    if last_dot < 0:
        return var_name
    return var_name[last_dot + 1:]
