import sys
import logging
import telegram
from telegram.ext import Updater, CommandHandler

from config import config, require_permission
import osrs
import greet
import database
import util
from cmdlogging import logged_command

@logged_command
def cmd_start(bot, update):
	#print('/start')
	update.message.reply_text('Greetings, mortal.')

@logged_command
@require_permission('operator')
def cmd_config(bot, update):
	#print('/config')
	update.message.reply_text('Configured')

@logged_command
def cmd_help(bot, update):
	#print('/help')
	update.message.reply_text('I can serve you in the following ways:\n' + \
		'/stats <name> - Lookup player stats\n' + \
		'/ge <item> - Lookup item on [GE](http://services.runescape.com/m=itemdb_oldschool/)\n' + \
		'/greeting - Configure new memeber greeting*\n' + \
		'*Must be admin of group chat',
		parse_mode='Markdown'
	)

stat_format = '''[{name}]({url}):
```
{ATT:>2}  ATK| {HIT:>2}   HP| {MIN:>2} MINE
{STR:>2}  STR| {AGI:>2}  AGI| {SMI:>2} SMTH
{DEF:>2}  DEF| {HER:>2} HERB| {FIS:>2} FISH
{RAN:>2} RNGE| {THI:>2} THVG| {COO:>2} COOK
{PRA:>2} PRAY| {CRA:>2} CRFT| {FIR:>2} FIRE
{MAG:>2} MAGE| {FLE:>2} FLET| {WOO:>2} WOOD
{RUN:>2}   RC| {SLA:>2} SLAY| {FAR:>2} FARM
{CON:>2} CONS| {HUN:>2} HUNT|    {OVE:>4}```'''
@logged_command
@util.send_action(telegram.ChatAction.TYPING)
def cmd_stats(bot, update, args):
	#print('/stats')
	if len(args) == 0:
		update.message.reply_text('Please use /stats followed by the name of ' + \
			'the player you wish to look up.')
		return

	player = ' '.join(args)
	#print('Looking up...')
	hiscore = osrs.hiscores.HiscoreResult.lookup(player)
	#print('Done!')
	if hiscore:
		kwargs = {
			'name': player,
			'url': osrs.hiscores.HiscoreResult.get_full_url(player)
		}
		for label in osrs.hiscores.HiscoreResult.skill_labels:
			kwargs[label[:3].upper()] = hiscore.skills[label].level
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

@logged_command
@util.send_action(telegram.ChatAction.TYPING)
def cmd_ge(bot, update, args):
	#print('/ge')
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

def handle_error(bot, update, error):
	logging.error(str(error))
	update.message.reply_text('I\'m sorry, there seems to be a magical force ' + \
		'preventing me from doing my job. I have alerted my master.')

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
	updater.dispatcher.add_handler(CommandHandler('config', cmd_config))
	updater.dispatcher.add_handler(CommandHandler('help', cmd_help))
	updater.dispatcher.add_handler(CommandHandler('stats', cmd_stats, pass_args=True))
	updater.dispatcher.add_handler(CommandHandler('ge', cmd_ge, pass_args=True))
	updater.dispatcher.add_error_handler(handle_error)

	# Greeting
	greet.setup_dispatcher(updater.dispatcher)

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
