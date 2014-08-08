import importers
import simpler

__author__ = 'Oded'

if __name__ == '__main__':
    main_module = 'throw.main'
    package_path = r'C:\Users\Oded\Desktop\throw-0.1-28-gd3ab'
    code = importers.flat_module(package_path, main_module)
    print simpler.make_simple(code)