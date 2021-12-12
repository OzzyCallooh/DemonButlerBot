CONFIG = config/default.config.json

run : venv
	$(VENV)/python src/demonbutler.py $(CONFIG)

include dev/Makefile.venv/Makefile.venv
