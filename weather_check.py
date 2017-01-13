#!/usr/bin/python

"""
    Simple module to pull out the liklihood of rain within the next 15 hours.

    Requires:
     - API Secret key
     - latitude, Longitude
     - Hours to look ahead when determining forecast

    Returns:
     - 0 for no need to salt
     - 1 for need to salt
     - negative numbers for errors

    Documentation on the Darksky API is available here:
     https://darksky.net/dev/
"""

# pylint: disable=C0103

import argparse
import logging
import requests


def retrieve_forecast(secret_key,
                      latitude,
                      longitude,
                      hours_from_now):
    """
        Pull a forecast for a specific location from Darksky.
    """
    if (secret_key is None or latitude is None or
            longitude is None or hours_from_now is None):
        logging.error('You haven\'t provided one or more required arguments')
        exit(-1)

    url_base = 'https://api.darksky.net/forecast'

    excludes = 'flags,currently,minutely,daily,alerts'
    units = 'si'
    payload = {
        'exclude': excludes,
        'units': units
        }

    r = requests.get('{base}/{secret}/{latitude},{longitude}'.format(
        base=url_base,
        secret=secret_key,
        latitude=latitude,
        longitude=longitude), params=payload)
    logging.debug('Compiled URL: %s', r.url)
    logging.debug('Response Code: %d', r.status_code)

    if r.status_code == 200:
        need_salt = parse_request(r.json(), hours_from_now)
    else:
        logging.error('Something broke whilst attempting to retrieve a '
                      'forecast')
        exit(-2)

    return need_salt


def parse_request(response_data=None, hours_from_now=15):
    """
        We just want to know if there is a liklihood of rain between 1700h and
        0800h with a temperature below 0 degrees so we know we should spread
        some salt...
    """
    logging.debug('response_data parsing:')
    if hours_from_now > 48:
        # We only have 48 hours of forecast data, limit to that
        hours_from_now = 48

    if response_data is None:
        raise IOError('Unable to retrieve forecast')

    hourly_data = response_data['hourly']['data']
    logging.debug(hourly_data)

    lay_salt = True
    too_much_precip = False

    for item in range(0, hours_from_now - 1):  # Decrement for 0 based list
        precip_prob = hourly_data[item]['precipProbability']
        precip_intensity = hourly_data[item]['precipIntensity']
        temperature = hourly_data[item]['temperature']
        dewpoint = hourly_data[item]['dewPoint']

        logging.debug('\n')
        logging.debug('Chance of Rain (out of 1): %s,', precip_prob)
        logging.debug('Intensity of Rain (out of 1): %s,', precip_intensity)
        logging.debug('Temp: %s,', temperature)
        logging.debug('Dew Point: %s,', dewpoint)

        if (temperature <= 0 and  # Chance of frost
                (temperature <= dewpoint or
                 (precip_prob > 0 and precip_prob <= 0.5 and
                  precip_intensity <= 0.3))):
            # The above checks that its below freezing, and that either we are
            # likely to see a dew/frost, or that its likely to rain lightly...
            # Its worth laying some salt!
            lay_salt = True
            logging.debug('Salt should be laid')
        else:
            lay_salt = False
            logging.debug('Salt should not be laid')
            # return lay_salt

        if precip_prob > 0.5 and precip_intensity > 0.3:
            # Its likely to rain enough to wash away any salt we lay down
            too_much_precip = True

    return lay_salt and not too_much_precip


if __name__ == "__main__":

    parser = argparse.ArgumentParser(
        description='Find out if we need to layout salt for ice the next'
        ' morning')

    parser.add_argument(dest='hours_from_now',
                        type=int,
                        default=15,
                        help='How many hours from now do we need to check?')

    parser.add_argument(dest='latitude',
                        type=float,
                        help='Latitude in decimal form, i.e 51.123456')

    parser.add_argument(dest='longitude',
                        type=float,
                        help='Longitude in decimal form, i.e. -1.123456')

    parser.add_argument('--log',
                        type=str,
                        required=False,
                        help='Set log level to:'
                        ' DEBUG, INFO, WARNING, ERROR, CRITICAL')

    parser.add_argument('--quiet',
                        dest='quiet',
                        action='store_true',
                        required=False,
                        help='Do not output result ot STDOUT')

    parser.set_defaults(quiet=False)

    parser.add_argument('--secret',
                        type=str,
                        required=True,
                        help='API Secret to authenticate against darksky.net,'
                        ' retrieve yours from https://darksky.net/dev/account')

    arguments = vars(parser.parse_args())

    logFormatStr = '%(levelname)s:%(asctime)s %(message)s'
    if arguments['log']:
        logging.basicConfig(format=logFormatStr, level=arguments['log'].upper())
    else:
        logging.basicConfig(format=logFormatStr)

    logging.info('Retrieving local weather forecast')


    salt_needed = retrieve_forecast(secret_key=arguments['secret'],
                                    latitude=arguments['latitude'],
                                    longitude=arguments['longitude'],
                                    hours_from_now=arguments['hours_from_now'])
    message = ''
    if salt_needed:
        # salt needed
        message = 'You need to lay out some salt tonight!'
        salt_needed = 1
    else:
        # salt not needed
        message = 'You don\'t need to worry about salt tonight.'
        salt_needed = 0

    logging.info(message)

    if not arguments['quiet']:
        print(message)

    exit(salt_needed)

