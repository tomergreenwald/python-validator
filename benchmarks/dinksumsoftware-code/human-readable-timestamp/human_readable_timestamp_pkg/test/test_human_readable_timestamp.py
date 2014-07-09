#!/usr/bin/env python

import sys
import os
# Put our parent directory (the package directory) on module search path
# e.g. we are /a/b/c/project-dir/package_dir/test/test_whatever.py
#      add    /a/b/c/project-dir/package_dir                      to sys.path
if sys.argv[0] :
    sys.path.insert(0,
                    os.path.abspath( os.path.join(os.path.dirname(sys.argv[0]),
                                                  "..")))


from human_readable_timestamp import HumanReadableTimeStamp, UTC
from datetime                 import datetime
import unittest


class TestHumanReadableTimeStamp(unittest.TestCase):
    # What we think things should be
    default_output_resolution = 'second'
    all_output_resolutions = ['day', 'hour', 'minute', 'second']
    all_output_resolutions.sort()

    # Molly's birthday works as a known time to test
    magic_moment = datetime(1990, 07, 23, 4, 23, 12, tzinfo=UTC())


    # Expected output of the magic moment
    # 1990-07-23 04:23:12+00:00
    expected_output = { 'day'     : '1990-07-23z',
                        'hour'    : '1990-07-23_T_04z',
                        'minute'  : '1990-07-23_T_04_23z',
                        'second'  : '1990-07-23_T_04_23_12z'
                       }
    

    def test_output_resolution(self):

        # Make sure default output resolution hasn't changed
        h=HumanReadableTimeStamp()
        self.assertEqual(h.default_output_resolution,
                        self.default_output_resolution,
                        "default output resolution is NOT:"+
                         self.default_output_resolution)


        # None=>Default output resolution
        h=HumanReadableTimeStamp()
        self.assertEqual(h.output_resolution,
                         self.default_output_resolution,
                         'Wrong default output resolution')

        # gibberish=>Exception
        self.assertRaises(ValueError, 
                          HumanReadableTimeStamp,
                          output_resolution="gibberish")

        # Make sure they didn't add/remove an output resolution
        h=HumanReadableTimeStamp()
        their_output_resolutions = h.format.keys()
        their_output_resolutions.sort()
        self.assertEqual( their_output_resolutions,
                          self.all_output_resolutions,
                          "Someone changed available output resolutions")


    def test_str_output(self):
        # Test all resolutions against expected output
        for out_fmt in self.all_output_resolutions :
            h = HumanReadableTimeStamp(self.magic_moment, out_fmt)
            self.assertEqual( h.str(),
                              self.expected_output[out_fmt],
                              "Wrong output for " + out_fmt + ":" + h.str())
                              

if __name__ == '__main__':
    unittest.main()

