import logging

from telegram.ext import CommandHandler, MessageHandler
from telegram.ext.filters import StatusUpdate
from sqlalchemy import Column, DateTime, String, BigInteger
from config import require_group_admin

import database
from cmdlogging import logged_command

GREETING_LENGTH_LIMIT = 512

class GreetConfig(database.Base):
	__tablename__ = 'greetconfig'
	tg_chatid = Column(BigInteger, primary_key=True)
	set_by = Column(BigInteger)
	greeting = Column(String(GREETING_LENGTH_LIMIT))

	def __init__(self, tg_chatid):
		self.tg_chatid = tg_chatid
		self.set_by = -1
		self.greeting = 'Welcome, mortal.'

def get_greeting(chat_id):
	session = database.dbsession()
	greetcfg = session.query(GreetConfig).filter(
		GreetConfig.tg_chatid == chat_id
	).one_or_none()
	return greetcfg.greeting if greetcfg else None

def im_in_a_new_chat(update, context):
	logging.info('Bot was added to chat: ' + str(update.effective_message.chat_id))
	update.message.reply_text('Hello, I am Alathazdrar the demon butler. ' + \
		' Thank you for hiring me for this group chat. I am at your service. ' + \
		' Type /help to see what I can do.')

def handle_new_chat_member(update, context):
	if len(update.message.new_chat_members) <= 0:
		return

	# Ignore bot additions
	has_non_bot = False
	for user in update.message.new_chat_members:
		if user.is_bot and user.id == context.bot.id:
			im_in_a_new_chat(update, context)
		if not user.is_bot:
			has_non_bot = True
			break
	if not has_non_bot:
		return

	greeting = get_greeting(update.message.chat_id)
	if greeting:
		#print('Sending greeting')
		update.message.reply_text(greeting)
	else:
		#print('Chat does not have greeting set')
		pass

@logged_command
@require_group_admin
def cmd_greeting(update, context):
	session = database.dbsession()

	# Query db for greeting
	greetcfg = session.query(GreetConfig).filter(
		GreetConfig.tg_chatid == update.message.chat_id
	).one_or_none()

	# Split message
	idx = update.message.text.find(' ')
	if idx == -1:
		reply = 'Type /greeting followed by what ' +\
			'you would like me to say when a new mortal joins this group.'
		if greetcfg:
			reply += ' The greeting for this group is:\n"{}"'.format(greetcfg.greeting)
			reply += ' \nDisable this greeting with /greeting delete.'
		else:
			reply += ' This group does not have a greeting set.'
		update.message.reply_text(reply)
		return
	greeting = update.message.text[idx+1:]

	# Determine action: delete or set
	if greeting.lower() == 'delete':
		if greetcfg:
			session.delete(greetcfg)
			session.commit()
			update.message.reply_text('As you wish. I will no longer greet new ' + \
				'members of this group.')
		else:
			update.message.reply_text('I am not presently instructed to greet ' + \
				'new members of this group.')
	elif len(greeting) > GREETING_LENGTH_LIMIT:
		update.message.reply_text('The length of this greeting is too great for ' + \
			'me to remember. I can only remember greetings that are {} characters or less; '.format(GREETING_LENGTH_LIMIT) + \
			'the one you provided is {} characters. Try using a link to a website like pastebin.org.'.format(len(greeting)))
	else:
		if not greetcfg:
			greetcfg = GreetConfig(update.message.chat_id)
		greetcfg.greeting = greeting
		greetcfg.set_by = update.message.from_user.id
		session.add(greetcfg)
		session.commit()
		update.message.reply_text('As you wish. I will greet new members of this ' + \
			'group with the following message:\n"{}"'.format(greeting))

def setup_application(application):
	application.add_handler(CommandHandler('greeting', cmd_greeting))
	application.add_handler(MessageHandler(
		callback=handle_new_chat_member,
		filters=StatusUpdate.NEW_CHAT_MEMBERS
	))