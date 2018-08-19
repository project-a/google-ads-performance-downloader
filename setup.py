from setuptools import setup, find_packages

setup(
    name='google-ads-performance-downloader',
    version='2.0.0',
    description="Downloads data from the Google Adwords Api to local files",

    install_requires=[
        'googleads==13.0.0',
        'click>=6.0',
        'wheel>=0.29'
    ],

    packages=find_packages(),

    author='Mara contributors',
    license='MIT',

    entry_points={
        'console_scripts': [
            'download-google-ads-performance-data=google_ads_downloader.cli:download_data',
            'refresh-google-ads-api-oauth2-token=google_ads_downloader.cli:refresh_oauth2_token'
        ]
    }
)
