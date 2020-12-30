from setuptools import setup

with open('README.md', mode='rt', encoding='utf-8') as f:
    readme = f.read()

extras_require = {
    'color': [
        'colorama>=0.4.3',
        'colorlog>=4.2.1'
    ]
}

# Setup module
setup(
    # Module name
    name='chronous',
    # Module version
    version='2.0.0b4',
    # License - MIT!
    license='MIT',
    # Author (Github username)
    author='Lapis0875',
    # Author`s email.
    author_email='lapis0875@kakao.com',
    # Short description
    description='Library for Event-Driven architecture using asyncio.',
    # Long description in REAMDME.md
    long_description=readme,
    long_description_content_type='text/markdown',
    # Project url
    project_urls={
        'Documentation': 'https://lapis0875.gitbook.io/chronous-docs',
        'Source': 'https://github.com/Lapis0875/Chronous/',
        'Tracker': 'https://github.com/Lapis0875/Chronous/issues',
        'Funding': 'https://www.patreon.com/lapis0875'
    },
    # Include module directory 'chronous'
    packages=['chronous', 'chronous.events', 'chronous.utils', 'chronous.sample'],
    py_modules=[],
    # Dependencies : This project use module 'colorlog', so add requirements.
    install_requires=['wheel>=0.35.1'],
    extras_require=extras_require,
    # Module`s python requirement
    python_requires='>=3.6',
    # Keywords about the module
    keywords=['Event-Driven architecture', 'EDD', 'async', 'asynchronous', 'asyncio'],
    # Tags about the module
    classifiers=[
        'License :: OSI Approved :: MIT License',
        'Operating System :: OS Independent',
        'Intended Audience :: Developers',
        'Natural Language :: English',
        'Natural Language :: Korean',
        'Development Status :: 2 - Pre-Alpha',
        'Programming Language :: Python :: 3.6',
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: Implementation :: CPython',
        'Framework :: AsyncIO',
        'Topic :: Software Development :: Libraries',
        'Topic :: Software Development :: Libraries :: Python Modules',
    ]
)
