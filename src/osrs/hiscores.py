import requests
from requests.models import PreparedRequest

from mwt import MWT
from util import shorten_number

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
	hiscore_full_url = 'https://secure.runescape.com/m=hiscore_oldschool/' + \
		'hiscorepersonal.ws'
	hiscore_url = 'https://secure.runescape.com/m=hiscore_oldschool/' + \
		'index_lite.ws'
	skill_labels = ['Overall', 'Attack', 'Defence', 'Strength', 'Hitpoints',
	'Ranged', 'Prayer', 'Magic', 'Cooking', 'Woodcutting', 'Fletching',
	'Fishing', 'Firemaking', 'Crafting', 'Smithing', 'Mining', 'Herblore',
	'Agility', 'Thieving', 'Slayer', 'Farming', 'Runecraft', 'Hunter',
	'Construction']
	score_labels = ['LMS', 'Bounty Hunter (hunter)', 'Bounty Hunter (rogue)', 
	'Clue Scrolls (all)', 'Clue Scrolls (beginner)', 'Clue Scrolls (easy)',
	'Clue Scrolls (medium)', 'Clue Scrolls (hard)', 'Clue Scrolls (elite)',
	'Clue Scrolls (master)']

	def __init__(self):
		self.skill_entries = []
		self.skills = {}
		for skill_label in HiscoreResult.skill_labels:
			skill_entry = SkillEntry(skill_label, 0, 0, 0)
			self.skill_entries.append(skill_entry)
			self.skills[skill_label] = skill_entry

		self.score_entries = []
		self.scores = {}
		for score_label in HiscoreResult.score_labels:
			score_entry = ScoreEntry(score_label, 0, 0)
			self.score_entries.append(score_entry)
			self.scores[score_label] = score_entry

	@staticmethod
	def parse(csv):
		self = HiscoreResult()
		lines = csv.split('\n')
		for line_no in range(0, len(lines)):
			# parse values on line as ints
			#print('line {}: {}'.format(line_no, lines[line_no]))
			values = [int(x) if x is not '' else 0 for x in lines[line_no].split(',')]
			if line_no >= 0 and line_no < 24:
				# lines[0] to lines[23] are skills
				idx = line_no
				skill_entry = self.skill_entries[idx]
				skill_entry.rank = values[0]
				skill_entry.level = values[1]
				skill_entry.xp = values[2]
				#print(str(skill_entry))
			elif line_no >= 24 and line_no < 34:
				# lines[24] to lines[34] are generic scores
				idx = line_no - 24
				score_entry = self.score_entries[idx]
				score_entry.rank = values[0]
				score_entry.score = values[1]
				#print(str(score_entry))
			else:
				pass
		return self

	@staticmethod
	@MWT(60*10)
	def lookup(player='Zezima'):
		res = requests.get(HiscoreResult.hiscore_url,
			params={ 'player': player },
			timeout=5
		)
		if res.status_code == 200:
			return HiscoreResult.parse(res.text)
		else:
			return None

	def get_full_url(player):
		req = PreparedRequest()
		req.prepare_url(HiscoreResult.hiscore_full_url, {'player': player})
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
