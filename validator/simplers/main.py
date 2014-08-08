import importers
import simpler

__author__ = 'Oded'

if __name__ == '__main__':
    main_module = 'fabric.main'
    package_path = r'C:\Users\Oded\Desktop\Fabric-1.3.4'
    code = importers.flat_module(package_path, main_module)
    print simpler.make_simple(code)