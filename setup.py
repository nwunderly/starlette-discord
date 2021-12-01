import setuptools
import re


with open('./README.md', 'r') as fp:
    long_description = fp.read()


with open('./starlette_discord/__init__.py', 'r') as fp:
    version = re.search(r'^__version__\s*=\s*[\'"]([^\'"]*)[\'"]', fp.read(), re.MULTILINE).group(1)


with open('requirements.txt') as f:
    requirements = f.read().splitlines()


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
    install_requires=requirements,
    extras_require={
        'docs': [
            'sphinx',
            'sphinxcontrib_trio',
            'myst_parser',
        ],
    },
    python_requires='>=3.8',
    packages=setuptools.find_packages(),
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

