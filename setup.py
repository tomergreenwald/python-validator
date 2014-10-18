from setuptools import setup, find_packages

setup(name='PythonValidator',
      version='1.0',
      description='Python Attributes Validator',
      author='Tomer G, Aviel A, Oded E',
      packages=find_packages(),

      install_requires=[
          'astor',
          'codegen',
          'tabulate'
      ],

      entry_points={'console_scripts': [
        'validator-example = validator.examples:main',
        'validate = validator.run_by_yourself:main'
    ]},
     )