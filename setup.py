from setuptools import setup, find_packages

setup(
    name="my_package",
    version="0.1.0",
    description="A reusable database connector with logging and DSN selection",
    packages=find_packages(),
    include_package_data=True,
    install_requires=[
        "pyodbc",
    ],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3",
        "Operating System :: Microsoft Windows",
    ],
)
