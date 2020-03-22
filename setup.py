import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="keckspec",
    version="0.0.1",
    author="Malena Rice",
    author_email="malena.rice@yale.edu",
    description="A package designed to return 18 stellar labels from input Keck HIRES spectra",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/users/malenarice/projects/1",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)
