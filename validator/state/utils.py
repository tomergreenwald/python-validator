import copy
import types

PRIMITIVES = set([eval('types.%s' %x) for x in dir(types) if x.endswith('Type')])

def is_primitive(obj):
    # sometime copy fails (for example when we create an empty class and look at its __init__ method
    # maybe the assumption of primitive in this case is not correct
    try:
        clone = copy.deepcopy(obj)
    except:
        return True
        
    try:
        clone.fdsfsdfdsfdsfdsfdsfdsfds = 5
        return False
    except:
        return True

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
