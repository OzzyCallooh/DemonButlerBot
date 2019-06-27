import requests
from requests.models import PreparedRequest
import datetime
from util import convert_short_number
from mwt import MWT

from osrs.itemaliases import alias

class PriceAmount(object):
	def __init__(self, amountInfo):
		self.trend = amountInfo['trend'] # positive, neutral, negative
		if type(amountInfo['price']) == str:
			self.price = convert_short_number(
				amountInfo['price'].replace('- ','-').replace(',','').strip()
			)
		elif type(amountInfo['price']) == int:
			self.price = amountInfo['price']

class PriceTrend(object):
	def __init__(self, trendInfo):
		self.trend = trendInfo['trend']
		self.change = convert_short_number(
			trendInfo['change'].replace('- ','-').replace(',','').strip()
		)

class PricePoint(object):
	def __init__(self, timestamp, price):
		self.timestamp = timestamp
		self.datetime = datetime.datetime.utcfromtimestamp(timestamp/1000)
		self.price = price

	def get_timestamp(self):
		return self.timestamp

	def get_price(self):
		return self.price

class PriceGraph(object):
	def __init__(self, priceInfo):
		self.points = []
		self.earliest = None
		self.latest = None
		self.highest = None
		self.lowest = None
		for timestampStr in priceInfo.keys():
			self.points.append(PricePoint(
				timestamp=int(timestampStr),
				price=priceInfo[timestampStr]
			))
		self.points.sort(key=PricePoint.get_timestamp)
		self.earliest = min(self.points, key=PricePoint.get_timestamp)
		self.latest = max(self.points, key=PricePoint.get_timestamp)
		self.highest = max(self.points, key=PricePoint.get_price)
		self.lowest = max(self.points, key=PricePoint.get_price)

class GEPriceGraphs(object):
	def __init__(self, pricesInfo):
		self.daily = PriceGraph(pricesInfo['daily'])
		self.average = PriceGraph(pricesInfo['average'])

class GEItemEntry(object):
	def __init__(self, itemInfo):
		self.id = itemInfo['id']
		self.icon = itemInfo['icon']
		self.icon_large = itemInfo['icon_large']
		self.type = itemInfo['type']
		self.type_icon = itemInfo['typeIcon']
		self.name = itemInfo['name']
		self.description = itemInfo['description']
		self.members = itemInfo['members']
		self.current = PriceAmount(itemInfo['current'])
		self.today = PriceAmount(itemInfo['today'])
		# Only appear on individual item searches
		if 'day30' in itemInfo:
			self.day30 = PriceTrend(itemInfo['day30'])
		if 'day90' in itemInfo:
			self.day90 = PriceTrend(itemInfo['day90'])
		if 'day180' in itemInfo:
			self.day180 = PriceTrend(itemInfo['day180'])

	def __str__(self):
		return '<Item: {name}>'.format(self.name)

	def get_graphs(self):
		return get_price_graphs(self.id)

class GESearchResult(object):
	def __init__(self, searchInfo):
		self.total = searchInfo['total']
		self.items = []
		for itemInfo in searchInfo['items']:
			self.items.append(GEItemEntry(itemInfo))

	def has_results(self):
		return len(self.items) > 0

	def is_empty(self):
		return not self.has_results()

	def first(self):
		return self.items[0] if self.has_results() else None

endpoint_item_search = 'http://services.runescape.com/m=itemdb_oldschool' + \
	'/api/catalogue/items.json'
@MWT(60*10)
def search_for_items(term):
	term = alias(term)

	res = requests.get(endpoint_item_search,
		params={'category': 1, 'page': 1, 'alpha': term.lower()}
	)
	if res.status_code == 200:
		search_result = GESearchResult(res.json())
		return search_result
	else:
		return None

endpoint_item_details = 'http://services.runescape.com/m=itemdb_oldschool' + \
	'/api/catalogue/detail.json'
@MWT(60*10)
def get_item_details(itemId):
	res = requests.get(endpoint_item_details, params={'item': itemId})
	if res.status_code == 200:
		item_entry = GEItemEntry(res.json()['item'])
		return item_entry
	else:
		#print(res.status_code, res.text)
		return None

endpoint_price_graph = 'http://services.runescape.com/m=itemdb_oldschool' + \
	'/api/graph/{itemId}.json'
@MWT(60*10)
def get_price_graphs(itemId):
	res = requests.get(endpoint_price_graph.format(itemId=itemId))
	if res.status_code == 200:
		return GEPriceGraphs(res.json())
	else:
		return None

url_item_page = 'http://services.runescape.com/m=itemdb_oldschool' + \
	'/viewitem'
def get_item_url(itemId):
	req = PreparedRequest()
	req.prepare_url(url_item_page, {'obj': itemId})
	return req.url