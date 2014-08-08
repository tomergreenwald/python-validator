def var_to_father(var_name):
    """
    converts var of form: f!g!h!x.a.b to be f!g!h!x.a
    """
    last_sep = var_name.rfind('!') + 1
    scope = var_name[:last_sep]
    base_name = var_name[last_sep:]
    last_dot = base_name.rfind('.')
    if last_dot < 0:
        return None
    father = base_name[:last_dot]
    return scope + father

def var_to_basename(var_name):
    """
    converts var of form: f!g!h!x.a.b to be b
    """
    last_sep = var_name.rfind('!') + 1
    scope = var_name[:last_sep]
    base_name = var_name[last_sep:]
    last_dot = base_name.rfind('.')
    return base_name[last_dot + 1:]
    