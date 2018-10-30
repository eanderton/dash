from setuptools import setup, find_packages

setup(
    name = 'dcsh',
    version = '1.0.0',
    url = 'https://github.com/eanderton/dcsh.git',
    author = 'Eric Anderton',
    author_email = 'eric.t.anderton@gmail.com',
    description = 'Configurable subshell for Docker Compose',
    packages = find_packages(),    
    install_requires = ['ansicolors', 'pyyaml'],
    entry_points = {
        'console_scripts': [
            'dcsh=dcsh.cli:main',
        ],
    },
)
