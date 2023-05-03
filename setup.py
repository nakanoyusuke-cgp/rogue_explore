from setuptools import setup, find_packages


setup(
    name="rogue_explore",
    version="1.0.0",
    packages=find_packages(),
    install_requires=[
        "gym==0.21.0", "tqdm", "numpy"
    ],
)
