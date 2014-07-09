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
import unittest
from tempfile import mkdtemp    # Make directory to test in
from shutil   import rmtree     # and remove it and it's contents

from dinkum_project import *




class Test_dinkum_project(unittest.TestCase):


    # Before each test*() called
    def setUp(self):
        ''' make a directory to work in and cd there'''
        self.test_dirname = mkdtemp()
        os.chdir( self.test_dirname )

        # Remember the search path for restoration on exit
        # Some tests munge it
        self.syspath_on_entry = sys.path

    # After each test*() called
    def tearDown(self):
        ''' Clean up what we made '''
        rmtree( self.test_dirname)

        # and what we mucked with
        sys.path = self.syspath_on_entry


    # Actual tests follow...

    def test_make_project_dir_0(self) :
        ''' make_project_dir() works with absolute pathname'''
        prj_name_in = "a-legal-project-name"
        prj_dir_in = os.path.join(self.test_dirname, prj_name_in)
        prj_dir,prj_name = make_project_dir(prj_dir_in)
                     
        self.assertEqual(prj_name, prj_name_in)
        self.assertEqual(prj_dir, prj_dir_in)
        self.assertTrue (self.is_legal_project_dir(prj_dir, prj_name))

    def test_make_project_dir_1(self) :
        ''' make_project_dir() works with relative pathname'''
        prj_name_in = "another-project-name-with-relative-pathname"
        prj_dir,prj_name = make_project_dir(prj_name_in)
                     
        self.assertEqual(prj_name, prj_name_in)
        self.assertEqual(prj_dir, os.path.abspath(prj_name_in))
        self.assertTrue (self.is_legal_project_dir(prj_dir, prj_name))


    def test_make_project_dir_2(self) :
        ''' make_project_dir() works with trailing separator '''
        prj_name_in = "project-name"

        #                                   "project-name/"
        prj_dir,prj_name = make_project_dir(prj_name_in + os.path.sep)
                     
        self.assertEqual(prj_name, prj_name_in)
        self.assertTrue (self.is_legal_project_dir(prj_dir, prj_name))


    def test_make_project_dir_3(self) :
        '''make_project_dir("" -or- "." -or- None) converts current directory.'''

        # Create and go a directory to convert
        new_dir = "should-be-converted-to-a-project-dir"
        os.mkdir(new_dir)
        os.chdir(new_dir)
        expected_prj_dir = os.path.abspath(".")

        for arg in [ "", ".", None ] :
            prj_dir,prj_name = make_project_dir(arg)
                     
            self.assertEqual(prj_name, new_dir)
            self.assertEqual(prj_dir, expected_prj_dir)
            self.assertTrue (self.is_legal_project_dir(prj_dir, prj_name))

    def test_make_project_dir_3(self) :
        '''make_project_dir() defaults to current directory.'''

        # Create and go a directory to convert
        new_dir = "should-be-converted-to-a-project-dir"
        os.mkdir(new_dir)
        os.chdir(new_dir)
        expected_prj_dir = os.path.abspath(".")

        prj_dir,prj_name = make_project_dir()
                     
        self.assertEqual(prj_name, new_dir)
        self.assertEqual(prj_dir, expected_prj_dir)
        self.assertTrue (self.is_legal_project_dir(prj_dir, prj_name))


    def test_make_python_package_dirs_0(self) :
        ''' make_python_package_dirs() one level'''
        prj_dir= "prj-dir"
        pkg_name_in = "pkg"

        pkg_dir, pkg_name = make_python_package_dirs(pkg_name_in, prj_dir )

        self.assertEqual(pkg_name, pkg_name_in)
        self.assertTrue (self.is_legal_package_dir(pkg_dir, pkg_name,prj_dir))

    def test_make_python_package_dirs_1(self) :
        ''' make_python_package_dirs() nested levels '''
        prj_dir= "prj-dir"
        pkg_name_in = "a.b.c.d.e.f.g.h"

        pkg_dir, pkg_name = make_python_package_dirs(pkg_name_in, prj_dir )

        self.assertEqual(pkg_name, pkg_name_in)
        self.assertTrue (self.is_legal_package_dir(pkg_dir, pkg_name,prj_dir))


    def test_make_python_package_dirs_1(self) :
        ''' make_python_package_dirs() defaults '''

        # Make a package with "current" directory as project directory
        # Create a project directory with a legal name and go there
        prj_name_in = "projectdir"
        prj_dir, prj_name = make_project_dir(prj_name_in)
        os.chdir( prj_dir )

        pkg_dir, pkg_name = make_python_package_dirs()

        prj_dir = os.path.join(pkg_dir, os.path.pardir)
        prj_dir = os.path.abspath(prj_dir)

        self.assertTrue( self.is_legal_project_dir(prj_dir, prj_name))
        self.assertEqual(pkg_name, prj_name)
        self.assertTrue( self.is_legal_package_dir(pkg_dir, pkg_name, prj_dir))


    def test_make_python_package_dirs_2(self) :
        ''' make_python_package_dirs() bad package names '''
        prj_dir= os.path.join(self.test_dirname, "project-with-bum-packages")

        pkg_name_in = "....."
        self.assertRaises( ErrorIllegalPackageName,
                           make_python_package_dirs,
                           *[pkg_name_in, prj_dir])

        pkg_name_in = "3abc"
        self.assertRaises( ErrorIllegalPackageName,
                           make_python_package_dirs,
                           *[pkg_name_in, prj_dir])

        pkg_name_in = "a.b.c.xxx_&_yyy"
        self.assertRaises( ErrorIllegalPackageName,
                           make_python_package_dirs,
                           *[pkg_name_in, prj_dir])



    def test_make_python_module_file_0(self) :
        '''make_python_module_file() legal module names'''

        # A module in top level module
        prj_dir = "test_prj_dir"
        pkg_name = "test_package"
        module_name = "good_module_name"
        (module_filename, module_name) = make_python_module_file(module_name,
                                                                 pkg_name, prj_dir )

        self.assertTrue (self.is_legal_module(prj_dir, module_filename, module_name))


        # A module deep in package heirarchy
        prj_dir = "test_prj_dir"
        pkg_name = "a.b.c.d.e.f.g.h.i.j.k.l.m.n"
        module_name = "deep_module"
        (module_filename, module_name) = make_python_module_file(module_name,
                                                                 pkg_name, prj_dir )

        self.assertTrue (self.is_legal_module(prj_dir, module_filename, module_name))
        

        # Almost all defaults
        module_name = "almost_all_defaults"
        (module_filename, module_name) = make_python_module_file(module_name)
        
        prj_dir = os.path.curdir  # Default project directory is current directory
        self.assertTrue (self.is_legal_module(prj_dir, module_filename, module_name))        


    def test_make_python_module_file_1(self) :
        '''make_python_module_file() bad module names'''

        # A capitol letter
        prj_dir = "test_prj_dir"
        pkg_name = "test_package"
        module_name = "Bad_module_name"

        self.assertRaises( ErrorIllegalPythonModuleName,
                           make_python_module_file,
                           *[module_name, pkg_name, prj_dir])

        # A digit
        prj_dir = "test_prj_dir"
        pkg_name = "test_package"
        module_name = "bad_module_name_3"

        self.assertRaises( ErrorIllegalPythonModuleName,
                           make_python_module_file,
                           *[module_name, pkg_name, prj_dir])


        # A special character
        prj_dir = "test_prj_dir"
        pkg_name = "test_package"
        module_name = "bad_mod-ule_name"

        self.assertRaises( ErrorIllegalPythonModuleName,
                           make_python_module_file,
                           *[module_name, pkg_name, prj_dir])

        
    def test_make_python_module_file_2(self) :
        '''make_python_module_file() unittest code'''
        
        # A module in top level module
        prj_dir = "test_prj_dir"
        pkg_name = "test_package"
        module_name_in = "module_name"
        (module_filename, module_name_out) = make_python_module_file(module_name_in,
                                                                     pkg_name, prj_dir )

        # Should have made a test/test_module_name"
        test_dir = os.path.join(os.path.dirname(module_filename),
                                "test")

        self.assertTrue ( os.path.isdir( test_dir) )

        test_module = os.path.join( test_dir, "test_" + module_name_in + ".py")
        self.assertTrue (os.path.exists(test_module))

        # <todo>
        # self.assertTrue (is_executable(test_module))
        
                                    
                       

    # Support functions
    def is_legal_project_dir(self, prj_dir, prj_name) :
        '''
        Returns True if "prj_dir" is valid a project directory
        for a project named "prj_name".
        '''

        # Must be an existing directory
        if not os.path.isdir(prj_dir) :
            return False    

        # pathname must end in project name
        if not prj_dir.endswith(prj_name) :
            return False

        # She be legal
        return True
        

    def is_legal_package_dir(self, pkg_dir, pkg_name, prj_dir) :
        '''
        Returns True if "pkg_dir" is valid a package directory
        for a package named "pkg_name" in "prj_dir"
        '''
        # Must be an existing directory
        if not os.path.isdir(prj_dir) :
            return False    

        # Must contain __init__.py
        magic_package_file = os.path.join(pkg_dir, "__init__.py")
        if not os.path.isfile (magic_package_file) :
            return False

        # Should be able to import the package
        return self.is_importable(prj_dir, pkg_name)

        

    def is_legal_module(self, project_dir, module_filename, module_name) :
        '''
        Returns True if "module_filename" is proper file representing
        a module named "module_name" in the project rooted in "project_dir"
        '''
        
        # File must exist
        if not os.path.isfile(module_filename) :
            return False

        # Module must be importable
        return self.is_importable(project_dir, module_name)
                             

    def is_importable(self, prj_dir, name) :
        '''
        Returns True if "name" is importable with "prj_dir"
        on the search path.

        "prj_dir" is added to beginning if sys.path
        '''

        sys.path.insert(0,prj_dir)
        __import__ (name)

        # She be importable
        return True


# Run the tests if invoked as script from command line
if __name__ == '__main__':
    unittest.main()


