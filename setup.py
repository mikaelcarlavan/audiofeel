import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="audiofeel",
    version="0.0.1",
    author="Simon Henrot & Mikael Carlavan",
    author_email="contact@mika-carl.fr",
    description="Audiofeel is open-source software for audio signal processing",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/mrAgan/audiofeel",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    install_requires=['pyaudio', 'numpy', 'scipy'],
)