__author__ = 'Oded'

import os

def read_module(package_path, module):
    path = package_path + '\\' + module.replace('.', '\\') + '.py'
    with open(path) as f:
        code = f.read()
    return code


def get_dependencies_dict(package_path, package_name, main_module):
    modules = [main_module]
    dependency = {}

    while modules:
        current = modules.pop()
        dependency[current] = []

        code = read_module(package_path, current)

        for code_line in code.splitlines():
            if code_line.startswith('import ' + package_name + '.'):
                raise Exception('Unsupported operation. Validator supports only "from" syntax')
            if code_line.startswith('from ' + package_name + '.') or code_line.startswith('from .'):
                from_, import_ = code_line.split('from ')[1].split(' import ')
                if code_line.startswith('from .'):
                    tmp = current.split('.')[len(from_.strip('.')) - len(from_) - 1:-1]
                    tmp.append(from_.strip('.'))
                    from_ = '.'.join(tmp)
                depencdencies = []
                if os.path.isdir(package_path + '\\' + from_.replace('.', '\\')):
                    for m in import_.split(', '):
                        depencdencies.append(from_ + '.' + m)
                else:
                    depencdencies.append(from_)

                dependency[current].extend(depencdencies)
                modules.extend(depencdencies)

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

    code = '\n'.join(filter(lambda line: not(line.startswith('from .') or line.startswith('from ' + package_name)),
                            code.splitlines()))
    print import_order
    for module in import_order:
        for m in module.split('.'):
            code = code.replace('%s.' % m, '')

    return code


def flat_module(package_path, main_module):
    package_name = main_module.split('.')[0]
    import_order = get_import_order(package_path, package_name, main_module)
    return flat(package_path, package_name, import_order)


if __name__ == '__main__':
    main_module = 'nilo.webgallery.runscript'
    package_path = r'C:\Users\Oded\Desktop\nilo.webgallery-0.2.5'
    print flat_module(package_path, main_module)