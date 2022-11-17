import re

from sqlalchemy import Column, BigInteger, String
from telegram.ext import CommandHandler

import database

class RememberedAccount(database.Base):
	__tablename__ = 'rememberedaccounts'

	tg_user_id = Column(BigInteger, primary_key=True)
	rs_username = Column(String(32))

	def __init__(self, tg_user_id, rs_username):
		self.tg_user_id = tg_user_id
		self.rs_username = rs_username

def get_remembered_account(tg_user_id, session=None):
	if session == None:
		session = database.dbsession()
	ra = session.query(RememberedAccount).filter(
		RememberedAccount.tg_user_id == tg_user_id
	).one_or_none()
	return ra

def get_rs_username(tg_user_id, session=None):
	if session == None:
		session = database.dbsession()
	ra = get_remembered_account(tg_user_id, session)
	return ra.rs_username if ra else None

invalid_rsn_chars = re.compile('[^\w _]')
def is_valid_rsn(rs_username):
	return re.search(invalid_rsn_chars, rs_username) == None

def cmd_remember(update, context):
	args = context.args
	rs_username = (' '.join(args))[:30]
	tg_user_id = update.message.from_user.id

	session = database.dbsession()
	if rs_username != '':
		# Set remembered username
		if not is_valid_rsn(rs_username):
			update.message.reply_text('That doesn\'t look like a valid RSN.')
			session.close()
			return

		ra = get_remembered_account(tg_user_id, session=session)
		if ra == None:
			ra = RememberedAccount(tg_user_id, rs_username)
		else:
			ra.rs_username = rs_username
		session.add(ra)
		session.commit()
		update.message.reply_text(
			'OK, I will remember your Old School RuneScape username (RSN): ' + \
			'*{}*\n\n'.format(
				rs_username
			) + \
			'I\'ll assume you want to use this name for commands like /skills from now on. ' + \
			'When you use /kc now, give me a hiscores label instead of an RSN. ' + \
			'You can tell me to /forget your RSN, or use /remember again to recall or change it.',
			parse_mode='Markdown'
		)

	else:
		rs_username = get_rs_username(tg_user_id)
		if rs_username:
			update.message.reply_text(
				'I am remembering this Old School RuneScape account username (RSN) for you: ' + \
				'*{}*\n\n'.format(
					rs_username
				) + \
				'You can tell me to /forget this, or use /remember again to recall or change it.',
				parse_mode='Markdown'
			)
		else:
			update.message.reply_text(
				'Put your Old School RuneScape account username (RSN) after the command and I\'ll remember it.'
			)
	session.close()

def cmd_forget(update, context):
	tg_user_id = update.message.from_user.id
	session = database.dbsession()
	ra = get_remembered_account(tg_user_id, session=session)

	if ra:
		session.delete(ra)
		session.commit()
		update.message.reply_text('OK, I forgot your Old School RuneScape account username (RSN). Set it again using /remember')
	else:
		update.message.reply_text('I am not remembering any Old School RuneScape account username (RSN) for you.')
	session.close()

def setup_application(application):
	application.add_handler(CommandHandler('remember', cmd_remember, pass_args=True))
	application.add_handler(CommandHandler('forget', cmd_forget))
