from setuptools import find_packages, setup

setup(
    name="lazerwfm",
    version="0.1.0",
    description="A flexible async workflow manager",
    author="LazerLabs",
    author_email="info@lazerlabs.pro",
    packages=find_packages(),
    install_requires=[
        "fastapi>=0.104.1",
        "uvicorn>=0.24.0",
        "pydantic>=2.5.1",
        "httpx>=0.25.2",
        "typer>=0.9.0",
        "rich>=13.7.0",
        "pyyaml>=6.0.1",
        "textual>=1.0.0",
    ],
    extras_require={
        "dev": [
            "pytest>=7.4.3",
            "pytest-asyncio>=0.23.2",
            "black>=23.11.0",
            "isort>=5.12.0",
            "mypy>=1.7.1",
            "ruff>=0.1.6",
        ],
    },
    entry_points={
        "console_scripts": [
            "lazerwfm=lazerwfm.cli:run_cli",
            "lazerwfm-server=lazerwfm.web.server:run_server",
            "lazerwfm-monitor=lazerwfm.monitor.app:main",
        ],
    },
    python_requires=">=3.10",
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
)
