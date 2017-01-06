# salt-forecast
Simple Darksky API powered script to check if you should put salt out to prevent a slip hazard the next morning


## Usage:
```console
$ python weather_check.py --help

positional arguments:
  hours_from_now   How many hours from now do we need to check?
  latitude         Latitude in decimal form, i.e 51.123456
  longitude        Longitude in decimal form, i.e. -1.123456

optional arguments:
  -h, --help       show this help message and exit
  --secret SECRET  API Secret to authenticate against darksky.net, retrieve
                   yours from https://darksky.net/dev/account

$ python weather_check.py 15 51.123456 -1.123456 --secret SomeSecretKeyHere!
2017-01-06 09:58:17,940 Retrieving local weather forecast
2017-01-06 09:58:17,943 Starting new HTTPS connection (1): api.darksky.net
2017-01-06 09:58:18,350 You don't need to worry about salt tonight.
```
