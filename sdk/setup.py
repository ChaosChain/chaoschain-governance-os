from setuptools import setup, find_packages

setup(
    name="chaoscore-sdk",
    version="0.1.0",
    description="Python SDK for the ChaosCore API Gateway",
    author="ChaosChain Labs",
    author_email="info@chaoschain.org",
    url="https://github.com/ChaosChain/chaoschain-governance-os",
    packages=find_packages(),
    install_requires=[
        "requests>=2.25.0",
    ],
    classifiers=[
        "Development Status :: 3 - Alpha",
        "Intended Audience :: Developers",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
    ],
    python_requires=">=3.9",
) 