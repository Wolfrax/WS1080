from distutils.core import setup

setup(
    name='WS1080',
    version='1.0',
    packages=['py'],
    url='www.viltstigen.se',
    license='GPL',
    author='Mats Melander',
    author_email='mats.melander@gmail.com',
    description='reading, storing and displaying data from weatherstation', requires=['pymongo']
)
