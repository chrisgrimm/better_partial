import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="better_partial",
    version="1.0.5",
    author="Christopher Grimm",
    author_email="cgrimm1994@gmail.com",
    description="A more intuitive way to partially apply functions in Python.",
    long_description="A more intuitive way to partially apply functions in Python.",
    long_description_content_type="text/markdown",
    url="https://github.com/chrisgrimm/better_partial",
    packages=setuptools.find_packages(),
    classifiers=(
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ),
)