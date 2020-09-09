from setuptools import setup, find_packages

# Setup module
setup(
    # Module name
    name="chronous",
    # Module version
    version="1.2.1",
    # License - MIT!
    license='MIT',
    # Author (Github username)
    author="Lapis0875",
    # Author`s email.
    author_email="lapis0875@kakao.com",
    # Short description
    description="Library for Event-Driven architecture using asyncio.",
    # Long description in REAMDME.md
    long_description=open('README.rst').read(),
    # Project url
    url="https://github.com/Lapis0875/Chronous",
    # Include module directory 'chronous'
    packages=find_packages(),
    # Dependencies : This project use module 'colorlog', so add requirements.
    install_requires=["colorama>=0.4.3", "colorlog>=4.2.1"],
    # Module`s python requirement
    python_requires=">=3.6",
    # Keywords about the module
    keywords=["Event-Driven architecture", "EDD", "async", "asynchronous", "asyncio"],
    # Tags about the module
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)
