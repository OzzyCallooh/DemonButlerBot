import sys
import json
from functools import wraps

config = None

if len(sys.argv) < 2:
	sys.stderr.write('Include config json file as first argument')
	sys.exit(1)

with open(sys.argv[1]) as f:
	config = json.loads(f.read())

async def get_admin_ids(bot, chat_id):
	admins = await bot.get_chat_administrators(chat_id)
	return [admin.user.id for admin in admins]

def require_group_admin(func):
	@wraps(wraps)
	async def wrapped(update, context, *args, **kwargs):
		user_id = update.effective_user.id
		chat_id = update.effective_chat.id

		admins = await get_admin_ids(context.bot, chat_id)
		if user_id in admins:
			return await func(update, context, *args, **kwargs)
		else:
			update.message.reply_text('I\'m sorry mortal, but I cannot honor that request.')
			return
	return wrapped

def get_user_perms(user):
	# Default to * permission entry
	perms = config['permissions']['*']
	# If entry exists by username or user id, use that instead
	if user.username in config['permissions']:
		perms = config['permissions'][user.username]
	if str(user.id) in config['permissions']:
		perms = config['permissions'][str(user.id)]
	return perms

def user_has_permission(user, permission):
	user_perms = get_user_perms(user)
	return permission in user_perms and user_perms[permission]

def require_permission(permission):
	def deco(func):
		@wraps(wraps)
		async def wrapped(update, context, *args, **kwargs):
			if user_has_permission(update.effective_user, permission):
				return await func(update, context, *args, **kwargs)
			else:
				await update.message.reply_text(config['permission_denied'])
				return

		return wrapped
	return deco