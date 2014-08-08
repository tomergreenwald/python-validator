__author__ = 'Oded'

import os


def read_module(package_path, module):
    path = package_path + '\\' + module.replace('.', '\\') + '.py'
    with open(path) as f:
        code = f.read()
    return code


def get_dependencies_dict(package_path, package_name, main_module):
    modules = set()
    modules.add(main_module)
    dependency = {}

    while modules:
        current = modules.pop()
        dependency[current] = []
        code = read_module(package_path, current)

        for code_line in code.splitlines():
            if code_line.startswith('import'):
                import_ = code_line.split('import ')[1]
                if os.path.isdir(package_path + '\\' + import_.replace('.', '\\')):
                    code_line = 'from %s import __init__' % import_
                elif os.path.isfile(package_path + '\\' + current[:current.rfind('.')] + '\\' + import_ + '.py'):
                    code_line = 'from %s import %s' % (current[:current.rfind('.')], import_)
                else:
                    code_line = 'from %s import *' % import_

            if code_line.startswith('from'):
                from_, import_ = code_line.split('from ')[1].split(' import ')
                if code_line.startswith('from .'):
                    tmp = current.split('.')[len(from_.strip('.')) - len(from_) - 1:-1]
                    tmp.append(from_.strip('.'))
                    from_ = '.'.join(tmp)

                tmp_path = package_path + '\\' + current[:current.rfind('.')] + '\\' + from_
                if os.path.isdir(tmp_path) or os.path.isfile(tmp_path + '.py'):
                    from_ = current[:current.rfind('.')] + '.' + from_

                if from_.startswith(package_name):
                    depencdencies = []
                    if os.path.isfile(package_path + '\\' + from_.replace('.', '\\') + '.py'):
                        depencdencies.append(from_)
                    elif os.path.isdir(package_path + '\\' + from_.replace('.', '\\')):
                        for m in import_.split(', '):
                            depencdencies.append(from_ + '.' + m)

                    dependency[current].extend(depencdencies)
                    for d in depencdencies:
                        if d not in dependency:
                            modules.add(d)

    return dependency


def order_imports(dependency_dict):
    modules = set()
    for module, depend_list in dependency_dict.iteritems():
        modules.add(module)
        for depend in depend_list:
            modules.add(depend)

    from collections import deque

    modules = deque(modules)
    import_order = []
    while modules:
        current_module = modules.popleft()
        can_import = True
        for d in dependency_dict[current_module]:
            if d in modules:
                can_import = False
        if can_import:
            import_order.append(current_module)
        else:
            modules.append(current_module)
    return import_order


def get_import_order(package_path, package_name, main_module):
    dependency_dict = get_dependencies_dict(package_path, package_name, main_module)
    imports_list = order_imports(dependency_dict)

    return imports_list


def flat(package_path, package_name, import_order):
    code = ''
    for module in import_order:
        code += read_module(package_path, module)
        code += os.linesep

    for module in import_order:
        for m in module.split('.'):
            code = code.replace('%s.' % m, '')

    return code


def flat_module(package_path, main_module):
    package_name = main_module.split('.')[0]
    import_order = get_import_order(package_path, package_name, main_module)
    return flat(package_path, package_name, import_order)