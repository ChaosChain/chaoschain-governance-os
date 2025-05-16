#!/usr/bin/env python3

from setuptools import setup, find_packages

setup(
    name="chaoscore-sdk",
    version="0.1.0",
    description="Python SDK for the ChaosCore platform",
    long_description=open("README.md").read(),
    long_description_content_type="text/markdown",
    author="ChaosChain Team",
    author_email="info@chaoschain.ai",
    url="https://github.com/chaoschain/chaoscore",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "crewai": ["crewai>=0.1.0"],
    },
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
    ],
    python_requires=">=3.8",
) 