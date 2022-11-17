from functools import wraps

def send_action(action):
	def deco(func):
		@wraps(func)
		async def wrapper(update, context, *args, **kwargs):
			await context.bot.send_chat_action(
				chat_id=update.effective_message.chat_id,
				action=action
			)
			return await func(update, context, *args, **kwargs)
		return wrapper
	return deco

def shorten_number(number):
	if number < 1000:
		return str(number)
	elif number < 100000:
		return '{:.1f}k'.format(number/1000)
	elif number < 1000000:
		return '{:.0f}k'.format(number/1000)
	elif number < 100000000:
		return '{:.1f}m'.format(number/1000000)
	else:
		return '{:.0f}m'.format(number/1000000)

key = {'%':.01,'k': 1000,'m':1000000,'b':1000000000}
def convert_short_number(s):
	if type(s) == int or type(s) == float:
		return s
	last_char = s[-1:]
	mult = 1
	if last_char in key:
		s = s[:-1]
		mult = key[last_char]
	return float(s) * mult