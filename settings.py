from pathlib import Path
from decimal import Decimal

def constants():

	TIME_FORMAT = "%I:%M %p" # Don't touch
	FILE_FORMAT = ".csv" # Don't touch

	const_ = {"TIME_FORMAT":TIME_FORMAT,"FILE_FORMAT":FILE_FORMAT}


	# Modify based on your preferences
	DEFAULT_RATE_PER_HOUR = Decimal("10.00") # <- Change rate here 
	MIN_RATE = Decimal("6.40")
	MAX_RATE = Decimal("50.00")
	DECIMAL_PLACE = 2
	DIGITS = 5
	DESKTOP_PATH = Path.home() / "Desktop" # Don't touch
	ONEDRIVE_TO_DESKTOP_PATH = Path.home() / "OneDrive" / "Desktop" # Don't touch

	const_.update(
		DEFAULT_RATE_PER_HOUR = DEFAULT_RATE_PER_HOUR,
		MIN_RATE = MIN_RATE,
		MAX_RATE = MAX_RATE,
		DECIMAL_PLACE = DECIMAL_PLACE,
		DESKTOP_PATH = DESKTOP_PATH,
		DIGITS = DIGITS,
		ONEDRIVE_TO_DESKTOP_PATH = ONEDRIVE_TO_DESKTOP_PATH)
	return const_

CONSTANTS = constants()
