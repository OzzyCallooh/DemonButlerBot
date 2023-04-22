"""
AccountType enum and utils to handle conversions.
"""

import enum

class AccountType(enum.Enum):
	ERROR = -1
	REGULAR = 0
	IRONMAN = 1
	HARDCORE_IRONMAN = 2
	ULTIMATE_IRONMAN = 3
	SKILLER = 4
	PURE = 5

def readable_account_type(account_type: AccountType) -> str:
	"""Prettifies the AccountType enum name.

	e.g. HARDCORE_IRONMAN -> Hardcore Ironman
	"""
	return ' '.join(account_type.name.split('_')).title()

account_type_aliases = {
	"": AccountType.REGULAR,
	"regular": AccountType.REGULAR,
	"standard": AccountType.REGULAR,
	"normie": AccountType.REGULAR,
	"ge": AccountType.REGULAR,
	"secretlysupportedbybots": AccountType.REGULAR,
	"vorkathfarmer": AccountType.REGULAR,
	"goldfarmer": AccountType.REGULAR,
	"pethunter": AccountType.REGULAR,
	"unrestricted": AccountType.REGULAR,
	"trader": AccountType.REGULAR,
	"traitor": AccountType.REGULAR,

	"iron": AccountType.IRONMAN,
	"fe": AccountType.IRONMAN,
	"ironman": AccountType.IRONMAN,
	"ironmeme": AccountType.IRONMAN,
	"ironwoman": AccountType.IRONMAN,
	"btw": AccountType.IRONMAN,
	"im": AccountType.IRONMAN,
	"grayhelm": AccountType.IRONMAN,
	"greyhelm": AccountType.IRONMAN,

	"hardcoreironman": AccountType.HARDCORE_IRONMAN,
	"hardcore_ironman": AccountType.HARDCORE_IRONMAN,
	"hardcoreiron": AccountType.HARDCORE_IRONMAN,
	"hardcoreironwoman": AccountType.HARDCORE_IRONMAN,
	"hcim": AccountType.HARDCORE_IRONMAN,
	"hc": AccountType.HARDCORE_IRONMAN,
	"hcbtw": AccountType.HARDCORE_IRONMAN,
	"coward": AccountType.HARDCORE_IRONMAN,
	"deathless": AccountType.HARDCORE_IRONMAN,
	"redhelm": AccountType.HARDCORE_IRONMAN,

	"ultimateironman": AccountType.ULTIMATE_IRONMAN,
	"ultimate_ironman": AccountType.ULTIMATE_IRONMAN,
	"uim": AccountType.ULTIMATE_IRONMAN,
	"bankless": AccountType.ULTIMATE_IRONMAN,
	"nobank": AccountType.ULTIMATE_IRONMAN,
	"masochist": AccountType.ULTIMATE_IRONMAN,
	"ihavetoomuchtime": AccountType.ULTIMATE_IRONMAN,
	"donttrustbanks": AccountType.ULTIMATE_IRONMAN,
	"badcredit": AccountType.ULTIMATE_IRONMAN,
	"pohfanatic": AccountType.ULTIMATE_IRONMAN,
	"valuablesack": AccountType.ULTIMATE_IRONMAN,

	"skiller": AccountType.SKILLER,
	"onlycans": AccountType.SKILLER,
	"skill": AccountType.SKILLER,
	"scaredofcombat": AccountType.SKILLER,
	"peacekeeper": AccountType.SKILLER,
	"nopvm": AccountType.SKILLER,
	"bownoarrow": AccountType.SKILLER,

	"pure": AccountType.PURE,
	"1def": AccountType.PURE,
	"pker": AccountType.PURE,
	"ieatalldamage": AccountType.PURE,
	"minmax": AccountType.PURE,
}

def str_to_account_type(account_type_str: str) -> AccountType:
	"""Convert common names to AccountType enum.

	Note that capitalization and spaces are unused. e.g. All of the following result in HARDCORE_IRONMAN
	* Hardcore Ironman
	* Hard Core Iron Man
	* hard coreiron man
	* hardcoreironman

	If it doesn't exist in the known aliases, return AccountType.ERROR.
	"""
	sanitized_str = account_type_str.replace(' ', '').lower()
	if sanitized_str in account_type_aliases:
		return account_type_aliases[sanitized_str]
	return AccountType.ERROR