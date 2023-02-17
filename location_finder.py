import os
from datetime import datetime
import logging

from shared_res import (santa_clara_county_zip, san_mateo_county_zip)
from zip_code_searches import get_locations_from_these_zipcodes

# make the archive directory
direc = 'zipcodes'
os.makedirs(direc, exist_ok=True)

# logging setup
t = datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')
log_str = 'zipcode_scraping_{:s}.log'.format(t)
log_str = os.path.join(direc, log_str)
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                    filename=log_str,
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')

# get the san mateo locations
get_locations_from_these_zipcodes(
    zipcodes=[int(x) for x in san_mateo_county_zip],
    save_dir=direc
)

# get the santa clara locations
# get_locations_from_these_zipcodes(
#     zipcodes=[int(x) for x in santa_clara_county_zip],
#     save_dir=direc
# )
