from setuptools import setup, find_packages

setup(
    name="minicompiler",
    version="0.1.0",
    description="A teaching compiler for a simplified C-like language",
    packages=find_packages(where="src"),
    package_dir={"": "."},
    python_requires=">=3.10",
    entry_points={
        "console_scripts": [
            "minicc=main:main",
        ],
    },
)