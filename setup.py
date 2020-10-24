import setuptools

with open("README.md", "r") as fh:
    long_description = fh.read()

setuptools.setup(
    name="autotrader-scraper", # Replace with your own username
    version="0.1.1",
    author="Suhail Idrees",
    author_email="idrees.suhail@gmail.com",
    description="Scraper for AutoTrader.co.uk",
    long_description=long_description,
    long_description_content_type="text/markdown",
    url="https://github.com/suhailidrees/autotrader_scraper",
    packages=setuptools.find_packages(),
    classifiers=[
        "Programming Language :: Python :: 3",
        "License :: OSI Approved :: MIT License",
        "Operating System :: OS Independent",
    ],
    python_requires='>=3.0',
)