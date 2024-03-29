# Demon Butler Bot

<img align="right" src="assets/demon-butler.png">

> Greetings, mortal! My task is to retrieve valuable information from the human game OldSchool RuneScape by Jagex Ltd, who of which I am not associated. I am at your eternal service.

&mdash; Alathazdrar, the demon butler

This is the repository for [@DemonButlerBot](https://t.me/DemonButlerBot), a [Telegram bot](https://core.telegram.org/bots) themed after the [Demon Butler](https://oldschool.runescape.wiki/w/Demon_butler) from [OldSchool RuneScape](https://oldschool.runescape.com/) by Jagex Ltd. He is created and managed by [Ozzy Callooh](https://github.com/OzzyCallooh) ([@OzzyC](https://t.me/OzzyC)).

## Commands

*	`/start`
	The butler will greet you!
*	`/help`
	Show a list of basic commands.
*	`/remember <name>`
	Tell the butler your RSN so it can remember it for name-based commands, or recall what you told the butler. You can also tell him to `/forget` it.
*	`/skills <name>`
	Looks up the stats of the player with the given `<name>`, or your remembered name. Example: `/stats Zezima`
*	`/kc <name>`, `/kc <name>, <label>`, or `/kc <label>` (after `/remember`)
	Show kill-counts for the name you provide, or a specific label if you told the butler to `/remember` your RSN, e.g. `/kc barrows`
	*	Outside of private chats, long messages won't send to prevent spam. You can override this by using `all` for `<label>`.
*	`/kchelp`
	Lists shortcut commands similar to `/kc` for groups of hiscore labels:
	*	`/gwd`, `/dks`, `/raids`, `/slayer`, `/f2p`, `/clues`, `/lms`
*	`/ge <item>`
	Looks up the current price of an item traded on the Grand Exchange.
*	`/greeting <greeting>`
	(Group admins only) Sets a greeting for the butler to say when a new person is added to a chat.
	*	`/greeting off`
		(Group admins only) Removes the group greeting.

## Dependencies

This bot runs on Python 3.5 or greater, and requires the following libraries:

*	[Python-Telegram-Bot](https://python-telegram-bot.org/)
*	[requests](https://2.python-requests.org/en/master/)

## Configuration

The Demon Butler uses [JSON](https://json.org) files to control how he operates. This is where information like the Telegram bot token should go. See [sample-with-comments.config.json](config/sample-with-conmments.config.json) for an example configuration file.

If `telegram.use_webhooks` is true, the bot will use an internal HTTP server to serve webhook requests. The bot will automatically set the webhook to `telegram.webhook.host` with port 443 (this cannot be configured). Use [nginx](https://www.nginx.com/) or [Apache](https://www.apache.org) to route SSL traffic to the internal port.

## Running the Bot

Set the `CONFIG` environment variable to point to your config file (default is `config/default.config.json`). Run the bot using GNU make. A virtual environment is automatically set up using [Makefile.venv](https://github.com/sio/Makefile.venv), which has other variables to configure like `PY` (default `python3`).

```bash
$ make run
````

## License

The Demon Butler Bot is licensed under [CC BY-NC-SA](https://creativecommons.org/licenses/by-nc-sa/4.0/).

![CC BY-NC-SA](https://licensebuttons.net/l/by-nc-sa/3.0/88x31.png)