from setuptools import setup, find_packages

setup(
    name='google-adwords-performance-downloader',
    version='1.6.1',

    description="Downloads data from the Google Adwords Api to local files",

    install_requires=[
        'googleads==10.0.0',
        'click>=6.0'
    ],

    packages=find_packages(),

    author='Mara contributors',
    license='MIT',

    entry_points={
        'console_scripts': [
            'download-adwords-performance-data=adwords_downloader.cli:download_data',
            'refresh-adwords-api-oauth2-token=adwords_downloader.cli:refresh_oauth2_token'
        ]
    }
)
