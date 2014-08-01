import os
import sys

from validator.state import AbstractState
from validator.state.exceptions import *

def wrap_check_attr(aa, vv, at):
    print 'checking var %s attr %s ...' %(vv, at),
    try:
        aa.check_attr(vv, at)
        print 'OK'
    except Exception as ee:
        print ee

class T(object):
    def __init__(self, tt):
        self.t = tt

a = AbstractState()
# x = 5
a.set_var_to_const('x', 5)

# y = T(6)
a.set_var_to_const('y', T(6))

# y.w = 8
a.add_var_attribute('y', 'w')
a.set_var_to_const('y.w', 8)

# z = T(2)
a.set_var_to_const('z', T(2))

wrap_check_attr(a, 'z', 't')
wrap_check_attr(a, 'z', 'w')
wrap_check_attr(a, 'y', 't')
wrap_check_attr(a, 'y', 'w')

# z = y
a.set_var_to_var('z', 'y')

wrap_check_attr(a, 'z', 'w')

# z.n = 5
a.add_var_attribute('z', 'n')
a.set_var_to_const('z.n', 5)

wrap_check_attr(a, 'y', 'n')

# z = x
a.set_var_to_var('z', 'x')

wrap_check_attr(a, 'y', 'n')
wrap_check_attr(a, 'z', 'n')
