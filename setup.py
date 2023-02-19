from setuptools import setup, find_packages


setup(
    name="rogue_explore",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "gym==0.26.2", "tqdm", "numpy"
    ],
)
