import setuptools


with open('./README.md', 'r') as fp:
    long_description = fp.read()


with open('./starlette_discord/__init__.py', 'r') as fp:
    # FIRST LINE:
    # __version__ = '<version>'
    line = fp.readline()
    version = eval(line[14:])


setuptools.setup(
    name='starlette-discord',
    author='nwunderly',
    url='https://github.com/nwunderly/starlette-discord',
    project_urls={
        "Documentation": "https://starlette-discord.rtfd.io/",
    },
    version=version,
    description='"Login with Discord" support for Starlette and FastAPI.',
    long_description=long_description,
    long_description_content_type='text/markdown',
    extras_require={
        'docs': [
            'sphinx',
            'sphinxcontrib_trio',
        ],
    },
    packages=setuptools.find_packages(),
    python_requires='>=3.8',
    classifiers=[
        'Development Status :: 2 - Pre-Alpha',
        'License :: OSI Approved :: MIT License',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Operating System :: OS Independent',
        'Programming Language :: Python :: 3.8',
        'Topic :: Internet',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Utilities',
    ],
)
