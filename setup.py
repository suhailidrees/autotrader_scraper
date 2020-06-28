import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="autotrader-scraper", # Replace with your own username
    version="0.1.0",
    author="Suhail Idrees",
    author_email="idrees.suhail@gmail.com",
    description="Scraper for AutoTrader.co.uk",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/suhail93/autotrader_scraper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=2.7',
)