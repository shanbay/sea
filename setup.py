import os
import re
import ast

import versioneer

from setuptools import setup, find_packages


_root = os.path.abspath(os.path.dirname(__file__))

with open(os.path.join(_root, 'requirements.txt')) as f:
    requirements = f.readlines()

with open(os.path.join(_root, 'README.md')) as f:
    readme = f.read()


def find_package_data(package):
    """
    Return all files under the root package, that are not in a
    package themselves.
    """
    walk = [(dirpath.replace(package + os.sep, '', 1), filenames)
            for dirpath, dirnames, filenames in os.walk(package)]

    filepaths = []
    for base, filenames in walk:
        filepaths.extend([os.path.join(base, filename)
                          for filename in filenames])
    return filepaths


setup(
    name='sea',
    version=versioneer.get_version(),
    cmdclass=versioneer.get_cmdclass(),
    description='shanbay rpc framework',
    long_description=readme,
    long_description_content_type='text/markdown',
    url='https://github.com/shanbay/sea',
    author='Michael Ding',
    author_email='yandy.ding@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: Web Environment',
        'Intended Audience :: Developers',
        'Operating System :: POSIX',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries :: Python Modules'
    ],
    keywords=['rpc', 'grpc'],
    packages=find_packages(exclude=['tests']),
    package_data={'sea': find_package_data('sea')},
    python_requires='>=3',
    install_requires=requirements,
    entry_points={
        'console_scripts': [
            'sea=sea.cli:main'
        ],
        'sea.jobs': [
            'async_task=sea.contrib.extensions.celery.cmd:async_task',
            'bus=sea.contrib.extensions.celery.cmd:bus'
        ]
    }
)
