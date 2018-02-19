# Changelog

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
