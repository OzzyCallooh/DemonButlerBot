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

VERSION = "1.1.0"

@logged_command
def cmd_start(update, context):
	update.message.reply_text('Greetings, mortal. Type /help to see a list of commands I can recognize.',
		parse_mode='Markdown',
		disable_web_page_preview=True
	)

@logged_command
def cmd_version(update, context):
	update.message.reply_text('I am DemonButlerBot, version ' + VERSION)

@logged_command
def cmd_help(update, context):
	update.message.reply_text('I can serve you in the following ways:\n' + \
		'/remember <name> - Tell me your RSN\n' + \
		'/skills <name> - Lookup player levels\n' + \
		'/kchelp - Explains /kc, which looks up boss kc\n' + \
		'/ge <item> - Lookup item on [GE](http://services.runescape.com/m=itemdb_oldschool/)\n' + \
		'/version - Show what version I\'m running\n' + \
		'\nFor group admins:\n' + \
		'/greeting - Set new member greeting',
		parse_mode='Markdown',
		disable_web_page_preview=True
	)

@logged_command
def cmd_kchelp(update, context):
	update.message.reply_text(
		'`/kc <name>`\n' + \
		'`/kc <name>, <label>`\n' + \
		'`/kc <label>` (if you used /remember)\n' + \
		'\n' + \
		'Looks up a name on the hiscores and queries one or more kill-count labels.' + \
		' For non-private chats, long results won\'t send unless you use "all" for the label.' + \
		'\n\nShortcuts:\n' + \
		'/clues - Clue Scroll completions (by tier)\n' + \
		'/lms - Last Man Standing rank\n' + \
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

cmd_args = re.compile('/\S+\s+(.+)')

non_alnum = re.compile('\W')
def make_hiscore_cmd(labels):
	assume_player_query = True
	if labels == None:
		labels = osrs.hiscores.HiscoreResult.score_labels
		assume_player_query = False

	kc_format = '''[{name}]({url}):'''
	@logged_command
	@util.send_action(telegram.ChatAction.TYPING)
	def cmd_kc(update, context):
		player = None
		label_input = 'all'
		implicit_all = False

		arg_str = None
		arg_match = re.match(cmd_args, update.message.text)
		if arg_match:
			arg_str = arg_match.group(1)

			if ',' in arg_str:
				# /kc Iron Yeen, Kree'Arra
				player, label_input = arg_str.split(',')
				player = player.strip()
				label_input = label_input.strip().lower()
				if label_input == '':
					label_input = 'all'
					implicit_all = True
			elif arg_str.strip().lower() == 'help':
				cmd_kchelp(update, context)
				return
			else:
				if assume_player_query:
					# /lms Salty Hyena
					player = arg_str.strip()
					label_input = 'all'
					implicit_all = True
				else:
					player = rememberaccount.get_rs_username(update.message.from_user.id)
					if player:
						# /kc Kree'Arra
						label_input = arg_str.strip().lower()
						if label_input == '':
							label_input = 'all'
							implicit_all = True
					else:
						# /kc MyFriendsRSN
						player = arg_str.strip()
						label_input = 'all'
						implicit_all = True
		else:
			# /kc
			player = rememberaccount.get_rs_username(update.message.from_user.id)
			implicit_all = True

			if not player:
				update.message.reply_text(
					'Put an Old School RuneScape account username (RSN) after the command.' + \
					' You can also tell me to /remember a specific RSN.' + \
					(' If you want a specific hiscore label too, put a comma and then the label.' if not assume_player_query else '') + \
					' Use /kchelp for more info.'
				)
				return

		logging.debug('player: {player}, label_input: {label_input}'.format(
			player=player,
			label_input=label_input
		))

		labels_lookup = None
		if label_input.lower() == 'all':
			labels_lookup = labels
		else:
			labels_lookup = []
			for label in labels:
				if re.sub(non_alnum, '', label_input).lower() in re.sub(non_alnum, '', label).lower():
					labels_lookup.append(label)
					if len(labels_lookup) >= 4:
						break

		if len(labels_lookup) == 0:
			update.message.reply_text(
				'I\'m not sure which hiscore labels you want.\n\n' + \
				'If you want to search for an RSN, put a comma at the end of your message.'
			)
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
				if count > 9 and update.message.chat.type != 'private' and implicit_all:
					update.message.reply_text(
						'I understood your request, but the result contained many hiscore labels. ' + \
						'Since this isn\'t a private chat, please use "all" for your label query to explicitly allow this.'
					)
					return

			if count > 0:
				message = ('\n' if len(lines) > 2 else ' ').join(lines)
				update.message.reply_text(
					message,
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
	updater.dispatcher.add_handler(CommandHandler('version', cmd_version))
	updater.dispatcher.add_handler(CommandHandler('kchelp', cmd_kchelp))
	updater.dispatcher.add_handler(CommandHandler('config', cmd_config))
	updater.dispatcher.add_handler(CommandHandler('skills', cmd_skills, pass_args=True))
	updater.dispatcher.add_handler(CommandHandler('stats', cmd_skills, pass_args=True))
	updater.dispatcher.add_handler(CommandHandler('kc', make_hiscore_cmd(None), pass_args=True))
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
	updater.dispatcher.add_handler(CommandHandler('lms', make_hiscore_cmd(['Last Man Standing (LMS)']), pass_args=True))
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
			url_path=config['telegram']['token'],
			cert=config['telegram']['webhook']['cert'],
			key=config['telegram']['webhook']['key'],
			webhook_url='https://' + config['telegram']['webhook']['host'] + \
			    '/' + config['telegram']['token'],
			drop_pending_updates=True
		)
	else:
		logging.debug('Start polling')
		updater.start_polling()
	updater.idle()

	logging.debug('Bot exiting')

if __name__ == '__main__':
	main(sys.argv)
