import os
import json
from datetime import datetime
from search_tools import (search_entire_zipcode, get_house_webpage,
                          extract_house_details, emit_message, stall_for_time)


def get_locations_from_these_zipcodes(
        zipcodes: list[int],
        save_dir: str):
    # get today's date:
    today = datetime.strftime(datetime.now(), '%Y%m%d')
    # check for the zipcodes already located
    zipcode_files = os.listdir(save_dir)
    searched_zipcodes = [int(f[:5]) for f in zipcode_files if 'locations' in f]
    search_these = [z for z in zipcodes if z not in searched_zipcodes]
    emit_message(' Locating in {: 3d} zipcodes'.format(len(search_these)),
                 'info')
    # go through the zipcodes that haven't been located
    for zipcode in search_these:
        # get all the recently sold locations
        sstr = ' Getting recently sold locations for '\
               'ZipCode {:d}'.format(zipcode)
        emit_message(sstr, 'info')
        locations = []
        try:
            locations = search_entire_zipcode(zipcode)
        except Exception as e:
            sstr = ' Location retrieval failed for zipcode {:d}'.format(zipcode)
            emit_message(sstr, 'warning')
            emit_message(' ' + str(e), 'error')
            if '403: Forbidden' in str(e):
                emit_message(' 403 error, waiting longer...', 'warning')
                stall_for_time(60, 70)
        if locations:  # not empty
            fn = os.path.join(
                save_dir,
                str(zipcode) + '_{:s}_locations.json'.format(today)
            )
            with open(fn, 'w') as jf:
                json.dump(locations, jf)
            emit_message(' Locations saved as {:s}'.format(fn), 'info')
        else:
            emit_message(' Locations was empty for {:d}'.format(zipcode),
                         'warning')
        # wait a bit to spare the servers
        stall_for_time(60, 70)  # this appears to be long enough


def get_houses_from_this_location_file(location_file: str, save_dir: str):
    emit_message(
        ' Getting houses from location file {:s}'.format(location_file), 'info')
    with open(location_file, 'r') as jf:
        locations = json.load(jf)
    n_houses = len(locations)
    emit_message(' Getting details on {:d} houses'.format(n_houses))
    houses = {}
    for n, location in enumerate(locations):
        try:
            webpage = get_house_webpage(location)
            houses[location] = extract_house_details(webpage=webpage)
        except Exception as e:
            sstr = ' Failed to detail location {:s}'.format(location)
            emit_message(sstr, 'warning')
            emit_message(' ' + str(e), 'error')
            if '403: Forbidden' in str(e):
                emit_message(' 403 error, waiting longer...', 'warning')
                stall_for_time(60, 70)
        else:
            sstr = ' {: 3d}/{: 3d} Retrieved house {:s}'.format(
                n + 1, n_houses, location)
            emit_message(sstr, 'info')
        stall_for_time(25, 35)
    emit_message(' Retrieved details on {:d} houses'.format(len(houses)))
    if houses:  # anything but empty
        zip = location_file.split(os.sep)[-1].split('_')[0]
        today = datetime.strftime(datetime.now(), '%Y%m%d')
        fn = os.path.join(save_dir, '{:s}_{:s}_houses.json'.format(zip, today))
        with open(fn, 'w') as jf:
            json.dump(houses, jf)
        emit_message('House details saved as {:s}'.format(fn), 'info')


def get_houses_from_the_location_files(n_max: int,
                                       save_dir: str):
    files = os.listdir(save_dir)
    location_files = [f for f in files if 'locations' in f]
    housed_zipcodes = [int(f[:5]) for f in files if 'houses' in f]
    search_these = [
        os.path.join(save_dir, f) for f in location_files
        if int(f[:5]) not in housed_zipcodes
    ]
    n = 0
    while n < n_max and n < len(search_these):
        emit_message(' Processing file {: 3d}/{: 3d}'.format(n + 1, n_max),
                     'info')
        get_houses_from_this_location_file(search_these[n], save_dir)
        n += 1
    emit_message(' Retrieved details for {:d} location file(s)'.format(n))
