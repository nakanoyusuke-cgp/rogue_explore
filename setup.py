from setuptools import setup, find_packages


setup(
    name="rogue_explore",
    version="0.1.0",
    packages=find_packages(),
    install_requires=[
        "gym", "tqdm", "numpy"
    ],
)
