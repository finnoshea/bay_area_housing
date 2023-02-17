import os
import logging
from datetime import datetime

from zip_code_searches import get_houses_from_the_location_files

n_files = 1000
direc = 'zipcodes'
os.makedirs(direc, exist_ok=True)

t = datetime.strftime(datetime.now(), '%Y%m%d_%H%M%S')
log_str = 'details_scraper_{:s}.log'.format(t)
log_str = os.path.join(direc, log_str)
logging.basicConfig(format='%(asctime)s:%(levelname)s:%(message)s',
                    filename=log_str,
                    level=logging.INFO,
                    datefmt='%Y-%m-%d %H:%M:%S')


get_houses_from_the_location_files(n_max=n_files, save_dir='zipcodes')