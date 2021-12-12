import sys
import re
import logging
import telegram
from telegram.ext import Updater, CommandHandler

from config import config, require_permission
import osrs
import database
import greet
import rememberaccount
import util
from cmdlogging import logged_command

VERSION = "1.0.0"

@logged_command
def cmd_start(update, context):
	update.message.reply_text('Greetings, mortal. Type /help to see a list of commands I can recognize.',
		parse_mode='Markdown',
		disable_web_page_preview=True
	)

@logged_command
def cmd_help(update, context):
	update.message.reply_text('I can serve you in the following ways:\n' + \
		'/remember <name> - Tell me your RSN\n' + \
		'/skills <name> - Lookup player levels\n' + \
		'/kc <name> - Lookup player boss kc\n' + \
		'/kchelp - Show kc shortcut commands\n' + \
		'/ge <item> - Lookup item on [GE](http://services.runescape.com/m=itemdb_oldschool/)\n' + \
		'\nFor group admins:\n' + \
		'/greeting - Set new member greeting',
		parse_mode='Markdown',
		disable_web_page_preview=True
	)

@logged_command
def cmd_kchelp(update, context):
	update.message.reply_text('I recognize the following kill-count commands. ' + \
		'Put the player\'s name after the command (or tell me to /remember yours):\n' + \
		'/kc - Show all kcs\n' + \
		'/kc <label> - Show one of your kcs (requires /remember)\n' + \
		'/gwd - God Wars Dungeon\n' + \
		'/raids - Raids (CoX, ToB)\n' + \
		'/slayer - Slayer Bosses\n' + \
		'/f2p - F2P Bosses (Obor, Bryo)\n' + \
		'/clues - Clue scrolls\n' + \
		'/wildy - Wilderness bosses',
		parse_mode='Markdown',
		disable_web_page_preview=True
	)

@logged_command
@require_permission('operator')
def cmd_config(update, context):
	update.message.reply_text('Nothing interesting happens.')

stat_format = '''[{name}]({url}):
```
{ATT:>2}  ATK  {HIT:>2}   HP  {MIN:>2} MINE
{STR:>2}  STR  {AGI:>2}  AGI  {SMI:>2} SMTH
{DEF:>2}  DEF  {HER:>2} HERB  {FIS:>2} FISH
{RAN:>2} RNGE  {THI:>2} THVG  {COO:>2} COOK
{PRA:>2} PRAY  {CRA:>2} CRFT  {FIR:>2} FIRE
{MAG:>2} MAGE  {FLE:>2} FLET  {WOO:>2} WOOD
{RUN:>2}   RC  {SLA:>2} SLAY  {FAR:>2} FARM
{CON:>2} CONS  {HUN:>2} HUNT     {OVE:>4}```'''
@logged_command
@util.send_action(telegram.ChatAction.TYPING)
def cmd_skills(update, context):
	args = context.args

	player = ' '.join(args)
	if len(args) == 0:
		player = rememberaccount.get_rs_username(update.message.from_user.id)
		if player == None:
			update.message.reply_text('Please use /skills followed by the name of ' + \
				'the player you wish to look up.')
			return

	hiscore = osrs.hiscores.HiscoreResult.lookup(player)
	if hiscore:
		kwargs = {
			'name': player,
			'url': osrs.hiscores.HiscoreResult.get_full_url(player)
		}
		for label in osrs.hiscores.HiscoreResult.skill_labels:
			level = hiscore.skills[label].level
			if level > 0:
				kwargs[label[:3].upper()] = hiscore.skills[label].level
			else:
				kwargs[label[:3].upper()] = ' -'
		update.message.reply_text(
			stat_format.format(**kwargs),
			parse_mode='Markdown',
			disable_web_page_preview=True
		)
	else:
		update.message.reply_text('Unfortunately, mortal, there is no such being ' + \
			'who goes by the name "{player}".'.format(
			player=player
		))


non_alnum = re.compile('\W')
def make_hiscore_cmd(labels):
	kc_format = '''[{name}]({url}):'''
	@logged_command
	@util.send_action(telegram.ChatAction.TYPING)
	def cmd_kc(update, context):
		args = context.args

		player = rememberaccount.get_rs_username(update.message.from_user.id)

		labels_lookup = labels

		if player == None:
			if len(args) > 0:
				player = ' '.join(args)
			else:
				update.message.reply_text('Please use /skills followed by the name of ' + \
					'the player you wish to look up.')
				return
		else:
			if len(args) > 0:
				arg = ' '.join(args)
				labels_lookup = []
				for label in labels:
					if re.sub(non_alnum, '', arg).lower() in re.sub(non_alnum, '', label).lower():
						labels_lookup.append(label)
						if len(labels_lookup) >= 4:
							break
				if len(labels_lookup) == 0:
					update.message.reply_text('I don\'t recognize what you are referring to.')
					return

		hiscore = osrs.hiscores.HiscoreResult.lookup(player)
		if hiscore:
			lines = []
			lines.append(kc_format.format(
				name=player,
				url=osrs.hiscores.HiscoreResult.get_full_url(player)
			))
			count = 0
			for label in labels_lookup:
				score_label = label
				if type(label) == tuple:
					score_label = label[0]
					label = label[1]

				score = hiscore.scores[score_label].score
				if score >= 0:
					count += 1
					lines.append('{label}: *{score}*'.format(
						label=label,
						score=score
					))
			if count > 0:
				update.message.reply_text(
					'\n'.join(lines),
					parse_mode='Markdown',
					disable_web_page_preview=True
				)
			else:
				update.message.reply_text(
					'That account is not ranked on the hiscores for that.',
					parse_mode='Markdown',
					disable_web_page_preview=True
				)
		else:
			update.message.reply_text('Unfortunately, mortal, there is no such being ' + \
				'who goes by the name "{player}".'.format(
				player=player
			))
	return cmd_kc

@logged_command
@util.send_action(telegram.ChatAction.TYPING)
def cmd_ge(update, context):
	args = context.args
	if len(args) == 0:
		update.message.reply_text('Please use /ge followed by the name of ' + \
			'the item for which you wish to search.')
		return
	itemSearchTerm = ' '.join(args)
	search_result = osrs.ge.search_for_items(itemSearchTerm)
	if search_result:
		itemEntry = search_result.first()
		if itemEntry:
			# Smart potion selection: choose (4) dose versions over (1)
			stemIdx = itemEntry.name.find('(1)')
			if stemIdx != -1:
				stem = itemEntry.name[:stemIdx]
				for otherEntry in search_result.items:
					if otherEntry != itemEntry and otherEntry.name[:stemIdx] == stem \
					   and otherEntry.name[stemIdx:] == '(4)':
						itemEntry = otherEntry
						break

			# Did you means
			didYouMean = ''
			if len(search_result.items) > 1:
				didYouMean += '\nDid you mean: '
				strs = []
				for i in range(1, min(4, len(search_result.items))):
					if search_result.items[i] != itemEntry:
						strs.append('[{name}]({url})'.format(
							name=search_result.items[i].name,
							url=osrs.ge.get_item_url(search_result.items[i].id)
						))
				didYouMean += ', '.join(strs)

			# Price graph has precise price
			priceGraphs = osrs.ge.get_price_graphs(itemEntry.id)
			if priceGraphs:

				update.message.reply_text(
					'Current price of [{name}]({url}): {price} gp'.format(
						name=itemEntry.name,
						price=util.shorten_number(priceGraphs.daily.latest.price),
						url=osrs.ge.get_item_url(itemEntry.id)
					) + didYouMean,
					parse_mode='Markdown'
				)
			else:
				update.message.reply_text(
					'Unfortunately, mortal, the Grand Exchange ' + \
						'failed to load the price graphs for [{name}]({url}).'.format(
						name=itemSearchTerm,
						url=osrs.ge.get_item_url(itemEntry.id)
					) + didYouMean,
					parse_mode='Markdown'
				)
		else:
			update.message.reply_text('Unfortunately, mortal, there is no such item ' + \
				'traded on the Grand Exchange with the name "{name}".'.format(
				name=itemSearchTerm
			))
	else:
		update.message.reply_text('Unfortunately, mortal, I could not access the ' + \
			'Grand Exchange prices for that item at this time.')

def handle_error(update, context):
	error = context.error
	logging.error(str(error))
	update.message.reply_text('I\'m sorry, there seems to be a magical force ' + \
		'preventing me from doing my job. I have alerted my master.')
	raise error

def main(argv):
	# Logging
	logging.basicConfig(level=config['logging']['level'])

	# Database
	logging.debug('Initializing database')
	database.init()

	# Updater
	logging.debug('Initializing updater')
	updater = Updater(token=config['telegram']['token'])
	updater.dispatcher.add_handler(CommandHandler('start', cmd_start))
	updater.dispatcher.add_handler(CommandHandler('help', cmd_help))
	updater.dispatcher.add_handler(CommandHandler('kchelp', cmd_kchelp))
	updater.dispatcher.add_handler(CommandHandler('config', cmd_config))
	updater.dispatcher.add_handler(CommandHandler('skills', cmd_skills, pass_args=True))
	updater.dispatcher.add_handler(CommandHandler('stats', cmd_skills, pass_args=True))
	updater.dispatcher.add_handler(CommandHandler('kc', make_hiscore_cmd(osrs.hiscores.HiscoreResult.score_labels), pass_args=True))
	updater.dispatcher.add_handler(CommandHandler('clues', make_hiscore_cmd(
		[
			('Clue Scrolls (beginner)','Beginner'),
			('Clue Scrolls (easy)','Easy'),
			('Clue Scrolls (medium)','Medium'),
			('Clue Scrolls (hard)','Hard'),
			('Clue Scrolls (elite)','Elite'),
			('Clue Scrolls (master)','Master'),
			('Clue Scrolls (all)', 'Total')
		]), pass_args=True)
	)
	updater.dispatcher.add_handler(CommandHandler('gwd', make_hiscore_cmd(['General Graardor', 'Kree\'Arra', 'Commander Zilyana', 'K\'ril Tsutsaroth']), pass_args=True))
	updater.dispatcher.add_handler(CommandHandler('dks', make_hiscore_cmd(
		[
			('Dagannoth Prime', 'Prime'),
			('Dagannoth Rex', 'Rex'),
			('Dagannoth Supreme', 'Supreme')
		]), pass_args=True)
	)
	updater.dispatcher.add_handler(CommandHandler('raids', make_hiscore_cmd(
		[
			'Chambers of Xeric', 'Chambers of Xeric (Challenge Mode)',
			'Theatre of Blood', 'Theatre of Blood (Hard Mode)'
		]), pass_args=True))
	updater.dispatcher.add_handler(CommandHandler('slayer', make_hiscore_cmd(['Grotesque Guardians', 'Cerberus', 'Kraken', 'Alchemical Hydra']), pass_args=True))
	updater.dispatcher.add_handler(CommandHandler('wildy', make_hiscore_cmd(['Crazy Archaeologist', 'Chaos Fanatic', 'Chaos Elemental', 'Scorpia', 'Venenatis', 'Vet\'ion', 'Callisto']), pass_args=True))
	updater.dispatcher.add_handler(CommandHandler('f2p', make_hiscore_cmd(['Obor', 'Bryophyta']), pass_args=True))
	updater.dispatcher.add_handler(CommandHandler('ge', cmd_ge, pass_args=True))
	updater.dispatcher.add_error_handler(handle_error)

	# Greeting
	greet.setup_dispatcher(updater.dispatcher)

	# Remember account
	rememberaccount.setup_dispatcher(updater.dispatcher)

	# Let's get started
	if config['telegram']['use_webhook']:
		logging.debug('Using webhook')
		updater.start_webhook(
			listen='127.0.0.1',
			port=config['telegram']['webhook']['internal_port'],
			url_path=config['telegram']['token']
		)
		updater.bot.set_webhook(
			url='https://' + config['telegram']['webhook']['host'] + \
			    '/' + config['telegram']['token'],
			certificate=open(config['telegram']['webhook']['cert'], 'rb')
		)
	else:
		logging.debug('Start polling')
		updater.start_polling()
	updater.idle()

	logging.debug('Bot exiting')

if __name__ == '__main__':
	main(sys.argv)
