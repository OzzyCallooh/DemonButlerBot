import requests
from requests.models import PreparedRequest

from mwt import MWT
from util import shorten_number
from osrs.accounttype import AccountType, readable_account_type

def rank_str(rank):
	if rank == -1:
		return 'unranked'
	else:
		return 'rank {}'.format(rank)

class SkillEntry(object):
	def __init__(self, label, rank, level, xp):
		self.label = label
		self.rank = rank
		self.level = level
		self.xp = xp

	def __str__(self):
		return '{label} level {level}: {xp} xp ({rank})'.format(
			label=self.label,
			xp=shorten_number(self.xp),
			rank=rank_str(self.rank),
			level=self.level
		)

class ScoreEntry(object):
	def __init__(self, label, rank, score):
		self.label = label
		self.rank = rank
		self.score = score

	def __str__(self):
		if self.score == -1:
			return '{label}: {rank}'.format(
				label=self.label,
				rank=rank_str(-1)
			)
		else:
			return '{label}: {score} ({rank})'.format(
				label=self.label, score=self.score,
				rank=rank_str(self.rank)
			)

class HiscoreResult(object):
	# The small changes needed for each account type for the URL.
	category_name = {
		AccountType.REGULAR: '',
		AccountType.IRONMAN: '_ironman',
		AccountType.HARDCORE_IRONMAN: '_hardcore_ironman',
		AccountType.ULTIMATE_IRONMAN: '_ultimate',
		AccountType.SKILLER: '_skiller',
		AccountType.PURE: '_skiller_defence',
	}
	# URL to attach to messages for users to read.
	hiscore_full_url = 'https://secure.runescape.com/m=hiscore_oldschoolCATEGORY/hiscorepersonal.ws'
	# URL to fetch hiscore values to be parsed.
	hiscore_url = 'https://secure.runescape.com/m=hiscore_oldschoolCATEGORY/' + \
		'index_lite.json'

	def __init__(self, payload):
		self.skill_entries = []
		self.skills = {}

		for skill_payload in payload['skills']:
			skill_entry = SkillEntry(
				skill_payload['name'],
				skill_payload['rank'],
				skill_payload['level'],
				skill_payload['xp']
			)
			self.skill_entries.append(skill_entry)
			self.skills[skill_payload['name']] = skill_entry

		self.score_entries = []
		self.scores = {}
		for score_payload in payload['activities']:
			score_entry = ScoreEntry(
				score_payload['name'],
				score_payload['rank'],
				score_payload['score']
			)
			self.score_entries.append(score_entry)
			self.scores[score_payload['name']] = score_entry

	@staticmethod
	@MWT(60*10)
	def lookup(player='Zezima', account_type: AccountType = AccountType.REGULAR):
		categoried_url = HiscoreResult.hiscore_url.replace('CATEGORY', HiscoreResult.category_name[account_type])
		res = requests.get(categoried_url,
			params={ 'player': player },
			timeout=5
		)
		if res.status_code == 200:
			return HiscoreResult(res.json())
		else:
			return None

	def get_full_url(player: str, rs_account_type: AccountType = AccountType.REGULAR):
		req = PreparedRequest()
		categoried_url = HiscoreResult.hiscore_full_url.replace('CATEGORY', HiscoreResult.category_name[rs_account_type])
		url_args = {
			'player': player, # Regular hiscores
			'user1': player,  # Other hiscores
		}
		req.prepare_url(categoried_url, url_args)
		return req.url

def main():
	import sys

	if len(sys.argv) < 2:
		print('First argument should be player name')
		sys.exit(1)

	player = sys.argv[1]
	hs = HiscoreResult.lookup(player=player)


if __name__ == '__main__':
	main()
