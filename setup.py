from setuptools import setup, find_packages

setup(
    name='sea',
    version='0.0.1',
    description='shanbay rpc framework',
    url='https://github.com/shanbay/sea',
    author='Michael Ding',
    author_email='yandy.ding@gmail.com',
    license='MIT',
    classifiers=[
        'Development Status :: 3 - Alpha',
        'Intended Audience :: Developers',
        'Topic :: Software Development :: Build Tools',
        'License :: OSI Approved :: MIT License',
        'Programming Language :: Python :: 3',
        'Programming Language :: Python :: 3.4',
        'Programming Language :: Python :: 3.5',
        'Programming Language :: Python :: 3.6',
    ],
    keywords='rpc',
    packages=find_packages(exclude=['tests']),
    test_suite="tests",
)
