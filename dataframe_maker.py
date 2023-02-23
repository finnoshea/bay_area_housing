import os
import json
import pandas as pd
import matplotlib.pyplot as plt

data = {}
for f in os.listdir('zipcodes'):
	if 'houses' in f:
		with open(os.path.join('zipcodes', f), 'r') as jf:
			data.update(json.load(jf))

df = pd.DataFrame.from_dict(data, orient='index')
df['location'] = df.index
df.index = range(len(df))

sfh = df[(df['sub_type'] == 'null') & (df['unit'] == 'null')]

bed_not_null = sfh['beds'] != 'null'
bath_not_null = sfh['baths'] != 'null'
county_is_santa_clara = sfh['county'] == 'Santa Clara'

ssfh = sfh[bed_not_null & bath_not_null & county_is_santa_clara].copy()


ssfh.loc[:, 'last_sold_date'] = pd.to_datetime(ssfh['last_sold_date'])
ssfh.loc[:, 'last_sold_price'] = pd.to_numeric(ssfh['last_sold_price'])
ssfh.loc[:, 'list_price'] = pd.to_numeric(ssfh['list_price'])
ssfh.loc[:, 'list_date'] = pd.to_datetime(ssfh['list_date']).dt.tz_localize(None)
ssfh.loc[:, 'baths'] = pd.to_numeric(ssfh['baths'])
ssfh.loc[:, 'beds'] = pd.to_numeric(ssfh['beds'])
ssfh.loc[:, 'sqft'] = pd.to_numeric(ssfh['sqft'])

ssfh['premium'] = 100 * (ssfh['last_sold_price'] - ssfh['list_price']) / ssfh['list_price']
ssfh['price_per_sqft'] = ssfh['last_sold_price'] / ssfh['sqft']


ssfh.to_csv('santa_clara_housing_data.csv')


med_last_sold_price = int(ssfh['last_sold_price'].median())
plt.scatter(ssfh['last_sold_date'], ssfh['last_sold_price'], marker='.')
plt.title('Santa Clara Co. SFH, median: ${:d}, N = {:d}'.format(med_last_sold_price, len(ssfh)))
plt.gca().axhline(med_last_sold_price, linestyle='dashed', color='k')
plt.yscale('log')
plt.xlabel('sell date')
plt.ylabel('sell price ($)')
plt.show()


plt.scatter(ssfh['last_sold_price'] / 1e6, ssfh['premium'], marker='.')
plt.title('Santa Clara Co., list vs sell price, N = {:d}'.format(len(ssfh)))
plt.xlabel('sold price (M$)')
plt.ylabel('premium over/under asking (%)')
plt.show()

med_premium = ssfh['premium'].median()
plt.hist(ssfh['premium'], bins=25)
plt.title('Santa Clara Co., Premiums, median: {:4.2f}%, N = {:d}'.format(med_premium, len(ssfh)))
plt.gca().axvline(med_premium, linestyle='dashed', color='k')
plt.xlabel('premium (%)')
plt.ylabel('count')
plt.show()


