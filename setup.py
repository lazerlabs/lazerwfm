from setuptools import find_packages, setup

setup(
    name="lazerwfm",
    version="0.1.0",
    description="A flexible async workflow manager",
    author="LazerLabs",
    author_email="info@lazerlabs.pro",
    packages=find_packages(),
    install_requires=[
        "asyncio>=3.4.3",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.7",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
    ],
)
