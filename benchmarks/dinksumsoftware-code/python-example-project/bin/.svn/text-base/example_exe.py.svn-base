#!/usr/bin/env python
''' Module docstring.
Not sure what goes here.
'''

import sys
import os

# Put our parent directory (the project directory) on module search path
# e.g. we are /a/b/c/project-dir/bin/example_exe.py
#      add    /a/b/c/project-dir                    to sys.path
if sys.argv[0] :
    sys.path.insert(0,
                    os.path.abspath( os.path.join(os.path.dirname(sys.argv[0]),
                                                  "..")))

from example_package.main_example_exe import main


if __name__ == "__main__":
    sys.exit(main())
