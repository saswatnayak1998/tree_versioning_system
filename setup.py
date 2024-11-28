from setuptools import setup, find_packages

setup(
    name="tree-manager",
    version="0.1.0",
    packages=find_packages(),
    install_requires=["sqlalchemy"],
    description="A tree structure management library for SQL databases.",
    author="Your Name",
    author_email="saswatxenon@gmail.com",
    url="git remote add origin https://github.com/saswatnayak1998/tree_versioning_system.git",
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires=">=3.7",
)
