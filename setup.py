from setuptools import setup, find_packages

setup(
    name="quboin",
    version="0.1.0",
    description="QUBO formulation of many problems.",
    author="Christos Kaldis",
    author_email="up1059364@upnet.gr",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
)
