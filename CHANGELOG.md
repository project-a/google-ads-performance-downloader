# Changelog

## 3.0.0 (2019-04-13)

- Change MARA_XXX variables to functions to delay importing of imports

**required changes** 

- If used together with a mara project, Update `mara-app` to `>=2.0.0`


## 2.1.0
*2019-01-23*

- Migrate into Adwords API version v201809
- Update googleads-python-lib to 15.0.2

## 2.0.0
*2018-08-19*

- Rename package to google-ads-performance-downloader
- Adapt code to reflect the renaming of Adwords to Google Ads
- Update googleads-python-lib to 13.0.0

**required changes**

- use new package names in requirements.txt
- adapt ETL to new ouput file names
- adapt calls to download cli command
 

## 1.7.1
*2018-05-02*

- Moved to googleads version 11.0.1
- uses now google_auth_oauthlib

## 1.7.0
*2018-03-12*
- Download currency information for each account


## 1.6.1
*2018-03-05*

- Made API version configurable


## 1.6.0
*2018-02-19*

- Moved to googleads version 10.0.0

## 1.5.1
*2018-01-29*

- Allow for arbitrary characters in account / campaign / ad group labels


## 1.5.0
*2018-01-19*

- Allow for spaces in account / campaign / ad group labels
- Retry in case of any error, not only HTTP 500


## 1.4.1
*2017-11-21*

- Updated googleads-python-lib to 9.0.0

## 1.4.0
*2017-10-23*

- Updated googleads-python-lib to 8.1.0


## 1.3.0 
*2017-10-10* 

- Updated googleads-python-lib to 8.0
-

## 1.2.0 
*2017-09-20* 

- Updated googleads-python-lib to 6.0 and use AdWords API version v201705
- Added retry logic
- Made the config and click commands discoverable in [mara-app](https://github.com/mara/mara-app) >= 1.2.0

**required changes**

- The file format changed to `v3`. Adapt etl scripts that process the output data.


## 1.1.1
*2017-06-30* 

- Updated googleads-python-lib to 6.0.0

## 1.1.0
*2017-06-07* 

- Updated googleads-python-lib to 5.6.0 and use AdWords API version v201705
