from setuptools import setup, find_packages

with open(file="README.md", mode="r") as readme_handle:
    long_description = readme_handle.read()

setup(
    name='job_offers_api',
    version='0.0.1',
    description='RestAPI to access data.',
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=find_packages(),
    python_requires=">=3.6",
    install_requires=[
        'pandas~=1.3',
        'SQLAlchemy~=1.4',
        'pymongo~=3.12',
        'shortuuid~=1.0',
        'Flask~=2.0',
        'python-dotenv~=0.19',
        'numpy~=1.21',
        'psycopg2~=2.9',
    ],
)
