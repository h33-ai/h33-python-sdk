from setuptools import setup, find_packages
import os

here = os.path.abspath(os.path.dirname(__file__))
with open(os.path.join(here, "README.md"), encoding="utf-8") as f:
    long_description = f.read()

setup(
    name="h33",
    version="0.1.0",
    description="H33 Post-Quantum Encryption SDK — Kyber + AES-256-GCM hybrid encryption, FHE biometrics, and more",
    long_description=long_description,
    long_description_content_type="text/markdown",
    author="H33.ai",
    author_email="sdk@h33.ai",
    url="https://h33.ai",
    license="MIT",
    packages=find_packages(),
    include_package_data=True,
    python_requires=">=3.8",
    install_requires=[
        "requests>=2.25.0",
    ],
    extras_require={
        "fhe": [],  # ctypes FFI to h33-fhe-client cdylib (no extra pip deps)
    },
    keywords=[
        "post-quantum", "encryption", "cryptography", "fhe",
        "homomorphic-encryption", "kyber", "dilithium", "biometrics",
        "zero-knowledge", "pqc", "ml-kem", "ml-dsa",
    ],
    project_urls={
        "Homepage": "https://h33.ai",
        "Documentation": "https://h33.ai/docs",
        "API Reference": "https://h33.ai/apis",
        "Benchmarks": "https://h33.ai/benchmarks",
        "White Paper": "https://h33.ai/white-paper",
        "Source": "https://github.com/h33-ai/h33-python-sdk",
        "Issues": "https://github.com/h33-ai/h33-python-sdk/issues",
    },
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Developers",
        "Intended Audience :: Science/Research",
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.8",
        "Programming Language :: Python :: 3.9",
        "Programming Language :: Python :: 3.10",
        "Programming Language :: Python :: 3.11",
        "Programming Language :: Python :: 3.12",
        "Topic :: Security :: Cryptography",
        "Topic :: Scientific/Engineering",
    ],
)
