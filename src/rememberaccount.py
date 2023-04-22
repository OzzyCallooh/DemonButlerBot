import re

from sqlalchemy import Column, BigInteger, String, Enum
from telegram.ext import CommandHandler

import database
import enum
from osrs.accounttype import AccountType, str_to_account_type, readable_account_type

class RememberedAccount(database.Base):
	__tablename__ = 'rememberedaccounts'

	tg_user_id = Column(BigInteger, primary_key=True)
	rs_username = Column(String(32))
	rs_account_type = Column(Enum(AccountType))

	def __init__(self, tg_user_id, rs_username: str, rs_account_type: AccountType):
		self.tg_user_id = tg_user_id
		self.rs_username = rs_username
		self.rs_account_type = rs_account_type

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

def get_rs_username_and_type(tg_user_id, session=None) -> tuple[str, AccountType]:
	"""Returns a tuple containing the remembered username and account type.

	If unavailable, this results in (None, None)
	"""
	if session == None:
		session = database.dbsession()
	ra = get_remembered_account(tg_user_id, session)
	return ra.rs_username, ra.rs_account_type if ra else (None, None)

invalid_rsn_chars = re.compile('[^\w _]')
def is_valid_rsn(rs_username):
	return re.search(invalid_rsn_chars, rs_username) == None

async def cmd_remember(update, context):
	"""Store the incoming player username from context into DB.

	context.arg will be assumed to have the form:

	rs username[, account_type]

	Where [, account_type] is optional.
	The username cannot be longer than 12 characters and the account type must
	be any cased version of account_type_aliases keys.
	e.g. Iron Hyger, Ironman
	"""
	# Reform the args from space separated to comma separated
	args = ' '.join(context.args).split(',')
	if len(args) > 2:
		await update.message.reply_text('You\'ve given me too many things to work with.')
		return

    # Trim everything after the first 12 characters as OSRS names cannot
    # exceed 12 characters.
	rs_username = args[0][:12] if args else ''

	rs_account_type = AccountType.REGULAR
	if len(args) > 1:
		rs_account_type = str_to_account_type(args[1])
		if rs_account_type == AccountType.ERROR:
			await update.message.reply_text('You\'ve given me an invalid account type: ' + args[1])
			return

	tg_user_id = update.message.from_user.id

	session = database.dbsession()
	if rs_username != '':
		# Set remembered username
		if not is_valid_rsn(rs_username):
			await update.message.reply_text('That doesn\'t look like a valid RSN.')
			session.close()
			return

		ra = get_remembered_account(tg_user_id, session=session)
		if ra == None:
			ra = RememberedAccount(tg_user_id, rs_username, rs_account_type)
		else:
			ra.rs_username = rs_username
			ra.rs_account_type = rs_account_type
		session.add(ra)
		session.commit()
		await update.message.reply_text(
			'OK, I will remember your Old School RuneScape username (RSN): ' + \
			'*{}* (*{}* account)\n\n'.format(
				rs_username, readable_account_type(rs_account_type)
			) + \
			'I\'ll assume you want to use this name for commands like /skills from now on. ' + \
			'When you use /kc now, give me a hiscores label instead of an RSN. ' + \
			'You can tell me to /forget your RSN, or use /remember again to recall or change it.',
			parse_mode='Markdown'
		)

	else:
		rs_username, rs_account_type = get_rs_username_and_type(tg_user_id)
		if rs_username:
			await update.message.reply_text(
				'I am remembering this Old School RuneScape account username (RSN) for you: ' + \
				'*{}* (*{}* account)\n\n'.format(
					rs_username, readable_account_type(rs_account_type)
				) + \
				'You can tell me to /forget this, or use /remember again to recall or change it.',
				parse_mode='Markdown'
			)
		else:
			await update.message.reply_text(
				'Put your Old School RuneScape account username (RSN) after the command and I\'ll remember it.'
			)
	session.close()

async def cmd_forget(update, context):
	tg_user_id = update.message.from_user.id
	session = database.dbsession()
	ra = get_remembered_account(tg_user_id, session=session)

	if ra:
		session.delete(ra)
		session.commit()
		await update.message.reply_text('OK, I forgot your Old School RuneScape account username (RSN). Set it again using /remember')
	else:
		await update.message.reply_text('I am not remembering any Old School RuneScape account username (RSN) for you.')
	session.close()

def setup_application(application):
	application.add_handler(CommandHandler('remember', cmd_remember))
	application.add_handler(CommandHandler('forget', cmd_forget))
