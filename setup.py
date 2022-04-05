import setuptools

from eat.__main__ import __version__

setuptools.setup(
    name='eat',
    version=__version__,
    description='Audio Encoding Toolkit',
    url='https://github.com/vevv/eat',
    author='vevv',
    author_email=None,
    license=None,
    packages=setuptools.find_packages(),
    package_data={
        "eat": ["py.typed", "data/*", "data/xml/*"]
    },
    entry_points={
        'console_scripts': ['eat=eat.__main__:main'],
    },
    install_requires=[
        'rich',
        'toml',
        'xmltodict',
    ],
    classifiers=[
        'Environment :: Console',
        'Operating System :: POSIX',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        'Programming Language :: Python :: 3.10',
        'Topic :: Utilities'
    ]
)
