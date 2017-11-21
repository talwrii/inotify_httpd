
import sys
try:
    # setuptools entry point is slow
    #  if we have festentrypoint use
    #  a fast entry point
    import fastentrypoints
except ImportError:
    sys.stdout.write('Not using fastentrypoints\n')
    pass


import setuptools
import os

HERE = os.path.dirname(__file__)

setuptools.setup(
    name='inotify_httpd',
    version="0.1.4",
    author='Tal Wrii',
    author_email='talwrii@gmail.com',
    description='',
    license='GPLv3',
    keywords='',
    url='',
    packages=['inotify_httpd'],
    long_description='See https://github.com/talwrii/inotify_httpd',
    entry_points={
        'console_scripts': ['inotify_httpd=inotify_httpd.inotify_httpd:main']
    },
    classifiers=[
        "License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)"
    ],
    test_suite='nose.collector',
    install_requires=['SimpleWebSocketServerFork==0.1.3', 'pyinotify'],
    )
