"""
Setup script for contextF library
"""

from setuptools import setup, find_packages

with open("README_PYPI.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setup(
    name="contextF",
    version="0.0.2",
    author="axondendrite",
    author_email="amandogra2016@gmail.com",
    description="Efficient context builder",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/adc77/contextF.git",
    packages=find_packages(),
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Topic :: Software Development :: Libraries :: Python Modules",
        "Topic :: Text Processing",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
    ],
    python_requires=">=3.8",
    install_requires=[
        "openai",
        "tiktoken",
        "langchain-text-splitters",
        "python-dotenv",
    ],
    extras_require={
        "pdf": ["pymupdf4llm"],
        "dev": [
            "pytest>=7.0.0",
            "pytest-cov>=4.0.0",
            "black>=22.0.0",
            "flake8>=5.0.0",
            "mypy>=1.0.0",
        ],
    },
    include_package_data=True,
    package_data={
        "contextF": ["default_config.json"],
    },
    entry_points={
        "console_scripts": [
            "contextf=contextF.cli:main",
        ],
    },
    keywords="context, documents, search, nlp, ai, text-processing",
    project_urls={
        "Bug Reports": "https://github.com/adc77/contextF/issues",
        "Source": "https://github.com/adc77/contextF",
        "Documentation": "https://github.com/adc77/contextF/blob/main/README.md",
    },
)
