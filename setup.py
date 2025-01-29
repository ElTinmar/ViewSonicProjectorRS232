from distutils.core import setup

setup(
    name='ViewSonicProjectorRS232',
    python_requires='>=3.8',
    author='Martin Privat',
    version='0.1.1',
    packages=[''],
    license='Creative Commons Attribution-Noncommercial-Share Alike license',
    description='Control Viewsonic pojector over serial',
    long_description=open('README.md').read(),
    install_requires=[
        "pyserial",
    ]
)