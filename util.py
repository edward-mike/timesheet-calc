import os
import csv 
import time
import click
import logging 
from pathlib import Path
from datetime import datetime
from typing import Optional, Tuple, List
from decimal import Decimal, getcontext
from rich.progress import track

from settings import CONSTANTS



# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler() 
    ]
)

getcontext().prec = CONSTANTS["DIGITS"]

date_formats = ["%d-%m-%Y", "%m-%d-%Y", "%Y-%m-%d"] # extend with other date formats
desired_date_format = date_formats[0] # using : %d-%m-%Y


def time_difference(*,
    time_in:str,
    time_out:str,
    date_:str) -> float:
    time_in = datetime.strptime(time_in, CONSTANTS["TIME_FORMAT"])
    time_out = datetime.strptime(time_out, CONSTANTS["TIME_FORMAT"])

    assert time_out > time_in,"clock out time must be greater than clock in time"

    time_diff = time_out - time_in

    time_diff_in_minutes = int(time_diff.total_seconds() / 60)
    time_diff_in_hours = round(time_diff_in_minutes/60,CONSTANTS["DECIMAL_PLACE"])

    if is_saturday(date_ = date_):
        time_diff_in_hours = time_diff_in_hours - 1

    return time_diff_in_hours


def time_difference_in_earning(*,
    time_in:str,
    time_out:str,
    date_:str,
    rate:float = None,
    ) -> Decimal:

    time_in_hr = time_difference(time_in=time_in,time_out=time_out,date_=date_)

    if rate is None:
        rate = CONSTANTS["DEFAULT_RATE_PER_HOUR"]

    # run a check on rate again :)
    assert _is_rate_correct(rate),f"{rate} is out of range for rate."

    return round(Decimal(time_in_hr) * Decimal(rate),2)



def is_saturday(*,date_:str) -> bool:

    # warning: use try/except instead of assertion
    assert type(date_) is str, f"{date_} must be a str date"

    try:
        date_obj = datetime.strptime(date_, desired_date_format)
        return date_obj.weekday() == 5
    except ValueError:
        return False



def _is_csv_file(file) -> bool:
	return file.endswith(CONSTANTS["FILE_FORMAT"])


def _is_rate_correct(rate):
	if rate <= 0:
		return True

	if CONSTANTS["MIN_RATE"] <= float(rate) <= CONSTANTS["MAX_RATE"]:
		return True
	return False


def _is_valid_directory() -> Tuple[Optional[str], bool]:
    if CONSTANTS["DESKTOP_PATH"].exists():
        logging.info(f"accessing file in directory {CONSTANTS["DESKTOP_PATH"]}")
        return CONSTANTS["DESKTOP_PATH"],True
    elif CONSTANTS["ONEDRIVE_TO_DESKTOP_PATH"].exists():
        logging.info(f"accessing file in directory {CONSTANTS["ONEDRIVE_TO_DESKTOP_PATH"]}")
        return CONSTANTS["ONEDRIVE_TO_DESKTOP_PATH"],True
    logging.error("the specified directory does not exist")
    return None, False



class RateError(Exception):
    pass

@click.command()
@click.option('--file_name', type=str, help="The file name to access.")
@click.option('--rate', default = CONSTANTS["DEFAULT_RATE_PER_HOUR"], type=float, help="Set the rate (default is set in settings to 10.00)")
def get_args_from_command(file_name: str,
    rate: float) -> Optional[Tuple[str, float]]:
	# Validate file and rate parameters for processing

    full_path = None

    def is_valid_rate(rate: float) -> None:
        if not (CONSTANTS["MIN_RATE"] <= float(rate) <= CONSTANTS["MAX_RATE"]):
            raise RateError(f"{rate} is out of range for rate.")
        

    def is_valid_file(file_name: str) -> None:
        
        nonlocal full_path

        path_, bool_ = _is_valid_directory()
        if not bool_:
            return

        full_path = path_/file_name

        # check csv file
        if not _is_csv_file(file_name):
            logging.error(f"{file_name} must be .csv")
            return

        
        def file_exists(file_full_path: str) -> None:
            try:
                if not file_full_path.exists():
                    raise FileNotFoundError(f"{file_full_path} does not exist.") 
                logging.info(f"accessing file: {file_full_path}")
            except FileNotFoundError:
                logging.error(f"{file_full_path} does not exist.")
                return False
            return True

        def is_file_readable(file_full_path: str) -> None:
            try:
                logging.info("checking file contents")
                with open(file_full_path, mode="r") as _:
                    return True 
            except (IOError,OSError) as exc:
                logging.error(f"checking file readability: {exc}")
            return False
            
        if not file_exists(full_path):
            return

        if not is_file_readable(full_path):
            return
        return True
   
    # Run a check on the file in directory
    if not is_valid_file(file_name):
        return None, None

    try:
        is_valid_rate(rate)
    except RateError as e:
        logging.error(e)
        return None, None

    return full_path,rate



def get_file_data(file_path:str) -> Optional[List[dict]]:
    from dateutil.parser import parse

    data = []

    try:
        with open(file_path,mode="r") as file:
            file_name = os.path.basename(file_path)
            logging.info("accessing file data")

            contents = csv.reader(file)

            #skip header 
            next(contents,None)

            # total rows in file
            file.seek(0)
            total_rows = sum(1 for row in contents)

            file.seek(0)
            next(contents,None)

            for row in contents:
                cleaned_row = [ value.strip() for value in row ]
                date_,time_in,time_out = cleaned_row
                # Fix : parse date not working as expected to.
                if parsed_date:= parse(date_):
                    reformatted_date = parsed_date.strftime(desired_date_format)
                    data.append({"date_":reformatted_date,"time_in":time_in,"time_out":time_out})
                else:
                    logging.error(f"unable to parse date: {date_}")

            def progressbar_(total_rows:int):
                for _ in track(range(total_rows-1), description='[green]Processing data'):
                    time.sleep(0.5)

            progressbar_(total_rows)

            logging.info(f"file {file_name} data accessed successfuly")
            logging.info(f"{total_rows - 1} records found in {file_name}")
            return data
    except FileNotFoundError:
        logging.error(f"File not found: {file_path}")
    except csv.Error:
        logging.error(f"CSV error while processing file ({file_name}")
    except Exception as exc:
        logging.error(f"Failed to access the data: {exc}")
    return data