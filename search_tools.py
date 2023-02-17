import re
from time import sleep
from random import randint
import logging
import urllib
from urllib.request import Request, urlopen

from typing import Optional


def emit_message(message: str, level: Optional[str] = None) -> None:
    allowed_levels = ['debug', 'info', 'warning', 'error', 'critical']
    if logging.getLogger().hasHandlers() and level in allowed_levels:
        method = getattr(logging, level)
        method(message)
    else:
        print(message)


def make_header() -> dict[str, str]:
    browsers = ['Mozilla', 'Safari', 'Chrome', 'Firefox']
    b = '{:s}/{:d}.{:d}'.format(
        browsers[randint(0, len(browsers) - 1)], randint(3, 7), randint(0, 8)
    )
    # return {'User-Agent': 'Mozilla/5.0'}
    return {'User-Agent': b}


def get_webpage(url: str) -> str:
    req = Request(url=url, headers=make_header())
    try:
        webpage = urlopen(req).read().decode()
    except urllib.error.HTTPError as e:
        emit_message(' ' + str(e), 'warning')
        if '403: Forbidden' in str(e):
            raise e
        return ''
    else:
        return webpage


def stall_for_time(t_min: int = 1, t_max: int = 5):
    r = randint(t_min, t_max)
    emit_message(' Waiting for {: 3d} seconds...'.format(r), 'info')
    sleep(r)

#--------------------------------------------------------
# for getting the results from a zipcode
#--------------------------------------------------------


def find_search_results(webpage: str) -> list[str]:
    p = re.compile("/realestateandhomes-detail")
    locs = []
    for m in p.finditer(webpage):
        locs.append(
            webpage[m.start():m.end() + 100].split('"')[0]
        )
    return locs


def recently_sold_zipcode_string(zipcode: int) -> str:
    first = 'https://www.realtor.com/realestateandhomes-search/'
    last = '/show-recently-sold'
    return ''.join([first, str(zipcode), last])


def add_page_to_zipcode_string(zip_string: str, page_num: int) -> str:
    # only known to work for single digit integers
    if page_num == 1:
        return zip_string
    else:
        return ''.join([zip_string, '/pg-' + str(page_num)])


def search_entire_zipcode(zipcode: int) -> list[str]:
    zip_string = recently_sold_zipcode_string(zipcode=zipcode)
    locations = []
    for page_num in range(1, 6):
        emit_message(' Looking at page {:d}'.format(page_num), 'info')
        zs = add_page_to_zipcode_string(zip_string=zip_string,
                                        page_num=page_num)
        webpage = get_webpage(zs)
        if webpage:  # not an empty string
            locs = find_search_results(webpage)
            locations.extend(locs)
        else:
            break
        stall_for_time(25, 35)
    return locations

#--------------------------------------------------------
# For getting the details of a single listing
#--------------------------------------------------------


def house_details_page_string(location: str) -> str:
    # location is an element of find_search_results or search_entire_zipcode
    first = 'https://www.realtor.com'
    return ''.join([first, location])


def get_house_webpage(location: str) -> str:
    loc_string = house_details_page_string(location)
    webpage = get_webpage(loc_string)
    return webpage


def extract_house_details(webpage: str) -> dict:
    data = {}
    p = re.compile("propertyDetails")
    for m in p.finditer(webpage):
        break
    q = re.compile("street_view_url")
    for n in q.finditer(webpage):
        break
    useful = webpage[m.start():n.end() + 2000]
    buffer = -2000  # makes some of the searches easier
    # get the address and coordinates
    match = re.search('"address":', useful[buffer:])
    address = useful[buffer + match.start():buffer + match.end() + 1000]
    data.update(parse_address(address))

    get_these = ['"beds"', '"baths"', '"sqft"', '"lot_sqft"',
                 '"median_listing_price"', '"last_sold_price"', '"list_date"',
                 '"last_sold_date"', '"list_price"', '"sub_type"']
    for gt in get_these:
        k = re.search(gt, useful)
        if k:  # if it was found
            data[gt.strip('"')] = \
                useful[
                k.start():k.end() + 50
                ].split(',')[0].split('":')[-1].strip('"')
        else:
            data[gt.strip('"')] = 'null'

    # association fee data
    j = re.search('Association:', useful)
    assoc = useful[j.start():j.end() + 200].split('","')
    if assoc[0].split()[-1] == 'Yes':
        data['association_fee'] = assoc[1].split()[-1]
        data['association_fee_frequency'] = assoc[2].split()[-1]
    else:
        data['association_fee'] = 'null'
        data['association_fee_frequency'] = 'null'

    return data


def parse_address(add_str: str) -> dict:
    dd = {}
    for elem in add_str.split(','):
        sa = elem.split(':')
        if sa[0] == '"address"':  # get the city name
            dd['city'] = sa[-1].strip('"')
        elif sa[0] == '"coordinate"':  # get latitude
            dd['lat'] = float(sa[-1])
        elif sa[0] == '"lon"':  # get longitude
            dd['long'] = float(sa[-1])
        elif sa[0] == '"postal_code"':  # get zipcode
            dd['zipcode'] = int(sa[-1].strip('"'))
        elif sa[0] == '"state_code"':  # get state abbreviation
            dd['state'] = sa[-1].strip('"')
        elif sa[0] == '"street_direction"':
            dd['street_direction'] = sa[-1].strip('"')
        elif sa[0] == '"street_name"':
            dd['street_name'] = sa[-1].strip('"')
        elif sa[0] == '"street_number"':
            dd['street_number'] = sa[-1].strip('"')
        elif sa[0] == '"street_post_direction"':
            dd['street_post_direction'] = sa[-1].strip('"')
        elif sa[0] == '"street_suffix"':
            dd['street_suffix'] = sa[-1].strip('"')
        elif sa[0] == '"unit"':
            dd['unit'] = sa[-1].strip('"')
        # county is a little trickier:
        dd['county'] = add_str.split('"county"')[-1].split(',')[1].split(':')[-1].strip('"')
    return dd


if __name__ == "__main__":
    with open('house_details.txt', 'r') as text_file:
        house = text_file.read()

