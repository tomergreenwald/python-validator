from setuptools import setup

setup(name='PythonValidator',
      version='1.0',
      description='Python Attributes Validator',
      author='Tomer G, Aviel A, Oded E',
      packages=['validator'],

      install_requires=[
          'astor',
          'codegen'
      ],

      entry_points={'console_scripts': [
        'validator-example = validator.examples:main',
        'validate = validator.run_by_yourself:main'
    ]},
     )