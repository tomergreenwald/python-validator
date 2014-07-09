import os
import stat
import errno
import string

# Some module wide definitions
_package_sep = '.'  # What separates python package names
_python_file_extension = os.extsep + "py"  # .py of <filename>.py



class Error(Exception):
    """Base class for exceptions in this module."""
    pass



def make_project_dir(project_dir=None) :
    if not project_dir : 
        # Use current directory
        project_dir = os.path.curdir

    # Handle project name only, e.g. "project-name" gets created in cwd
    # Handle trailing separator, e.g. "/a/b/project-name/
    project_dir = os.path.abspath(project_dir)

    # Extract and bless the project name
    project_name = os.path.basename( project_dir )
    is_legal_project_name(project_name)

    # Create the directory and it's parents if necessary
    try :
        os.makedirs( project_dir )
    except OSError, excptn :
        # It is ok if directory already exists
        if excptn.errno != errno.EEXIST :
            # otherwise, pass along the error
            raise 

    # We give back project_dir as absolute pathname
    return (project_dir, project_name)


def make_python_package_dirs(package_name=None, project_dir=None) :
    project_dir, project_name=make_project_dir(project_dir)

    # If caller didn't specify...
    if not package_name :
        # name the package from the project_name
        # whatever-i-was => whatever_it_was
        package_name = project_name.replace("-","_")

    # Iterate over package heirarchy from top to bottom
    package_parent_dir = project_dir
    for pkg_name in package_name.split(_package_sep) :

        # Bless the package_name
        is_legal_python_package_name(pkg_name)

        # Create the directory
        package_dir = os.path.join(package_parent_dir, pkg_name)
        try :
            os.mkdir(package_dir)
        except OSError, excptn :
            # It is ok if directory already exists
            # <todo> MAYBE confirm __init__.py exists there, error otherwise
            if excptn.errno != errno.EEXIST :
                # otherwise, pass along the error
                raise 

        # Create the magic file that makes it a package
        package_file = "__init__" + _python_file_extension
        package_file = os.path.join( package_dir, package_file)

        # Make it empty, and it's ok if it already exists
        open (package_file, "a").close()

        # Walk down the heirarchy
        package_parent_dir = package_dir

    return (package_dir,package_name)


def make_python_module_file(module_name, package_name=None, project_dir=None) :

    # Bless the inputs
    is_legal_python_module_name(module_name)

    # Create/locate the directories we need
    (project_dir, project_name) = make_project_dir(project_dir)
    (package_dir, package_name) = make_python_package_dirs(package_name, project_dir)


    # put together the filename: <package_path>/<module_name>.py
    module_filename = module_name + _python_file_extension
    module_filename = os.path.join( package_dir, module_filename )
    
    # prepend package heirarchy to modulename
    module_fullname = package_name + _package_sep + module_name

    # Make the module file empty, and it's ok if it already exists
    open (module_filename, "a").close()

    # Now create a directory/file to test it:
    # package_dir/test/test_<module_name>.py
    test_dir = os.path.join( package_dir, "test")
    try :
        os.makedirs( test_dir )
    except OSError, excptn :
        # It is ok if directory already exists
        if excptn.errno != errno.EEXIST :
            # otherwise, pass along the error
            raise 

    # test_<module_name>.py
    test_filename = "test_" + module_name + _python_file_extension
    test_filename = os.path.join(test_dir, test_filename)

    # Make an empty file, it's ok if it exists
    open (test_filename, "a").close()

    # Make it executable to all
    os.chmod(test_filename, stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH) 
    # ############ test this ##################

    return (module_filename, module_fullname,)




class ErrorIllegalProjectName(Error) :
    pass
def is_legal_project_name(project_name) :
    # <todo>  start with (lc letter) + (lc letters, digits, -)
    pass



class ErrorIllegalPackageName(Error) :
    pass

def is_legal_python_package_name(package_name) :
    # <todo> lower case, check and reference PEP
    try:
        is_legal_python_variable_name(package_name)
    except ErrorIllegalPythonVariableName, excptn :
        raise ErrorIllegalPackageName(excptn)



class ErrorIllegalPythonVariableName(Error) :
    pass

def is_legal_python_variable_name(variable_name) :
    
    if not variable_name :
        raise ErrorIllegalPythonVariableName(
            'Must exist, cannot be "" or None')

    # (underscore or letter) + (any number of letters, digits, or underscores)
    # case matters
    allowed_chars = '_' + string.letters
    if  not variable_name[0] in allowed_chars :
        raise ErrorIllegalPythonVariableName(
            "Does not start with _ or letter: `%s'"
            % variable_name)

    # Scan the remainder
    allowed_chars += string.digits
    for c in variable_name[1:] :
        if not c in allowed_chars :
            raise ErrorIllegalPythonVariableName(
                "Contains other than _, letter, or digit: `%s'"
                % variable_name)
    
    # She be legal


class ErrorIllegalPythonModuleName(Error) :
    pass

def is_legal_python_module_name(module_name) :

    if not module_name :
        raise ErrorIllegalModuleName('Must exist, cannot be "" or None')

    # PEP8: Modules should have short, all-lowercase names.
    # Underscores can be used in the module name if it improves readability.
    allowed_chars = '_' + string.lowercase

    for c in module_name :
        if not c in allowed_chars :
            raise ErrorIllegalPythonModuleName(
                "Contains other than _ or lower case letters: `%s'"
                % module_name)
    # module name is legal

    



