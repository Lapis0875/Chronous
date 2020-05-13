import setuptools

setuptools.setup(
    name="Chronous",
    version="1.0.0",
    license='MIT',
    author="Lapis0875",
    author_email="lapis0875@kakao.com",
    description="Aysnchronous Game library for discord.py",
    long_description=open('README.md').read(),
    url="https://github.com/Lapis0875/Chronous",
    packages=setuptools.find_packages(),
    classifiers=[
        # 패키지에 대한 태그
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent"
    ],
)