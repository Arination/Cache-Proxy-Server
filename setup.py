from setuptools import setup, find_packages

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

with open("requirements.txt", "r", encoding="utf-8") as fh:
    requirements = fh.read()

setup(
    name="caching-proxy",
    version="0.0.1",
    author="Puru Agarwal",
    author_email="puru.agar99@gmail.com",
    license=" GNU GENERAL PUBLIC LICENSE V3 (GPLV3)",
    description="<short description for the tool>",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/Puru80/Python-Pro",
    py_modules=["cahcing_proxy", "app"],
    packages=find_packages(),
    install_requires=[requirements],
    python_requires=">=3.7",
    classifiers=[
        "Programming Language :: Python :: 3.8",
        "LICENSE :: OSI APPROVED :: GNU GENERAL PUBLIC LICENSE V3 (GPLV3)",
        "Operating System :: OS Independent",
    ],
    entry_points="""
        [console_scripts]
        caching-proxy=caching_proxy:cli
    """,
)
