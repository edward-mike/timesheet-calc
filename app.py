from typing import List, Dict,Any
from rich.console import Console
from rich.table import Table
import logging 

from settings import CONSTANTS

from util import (get_args_from_command,
    get_file_data,
    time_difference,
    time_difference_in_earning)

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    handlers=[
        logging.StreamHandler() 
    ]
)

# NOte: Needs refactoring.
date_formats = ["%d-%m-%Y", "%m-%d-%Y", "%Y-%m-%d"] # extend with other date formats
desired_date_format = date_formats[0] # using : %d-%m-%Y


def pretty_table_for_totals(*,records:List[Dict[str, Any]]) -> Table:

    console = Console()
    table = Table(show_header=True, header_style="bold blue")

    # Header
    table.add_column("Total Days Worked", style="dim", width=16)
    table.add_column("Total Hours Worked")
    table.add_column("Total Earning")
    table.add_column("Rate Used",justify="right")


    data_sum = {
    "total_days": str(len(records)),
    "total_hours":0,
    "total_earning":0,
    "rate_used": str(CONSTANTS["DEFAULT_RATE_PER_HOUR"])
    }

    hr_total, earning_total = 0,0

    for record in records:
        date_, time_in, time_out = record.get("date_"), record.get("time_in"), record.get("time_out")

        data = {
        "time_in":time_in,
        "time_out":time_out,
        "date_":date_,
        }

        # computations
        per_duration = time_difference(**data)
        earning = time_difference_in_earning(**data)
        
        hr_total += per_duration
        earning_total += earning

    data_sum["total_hours"] = str(hr_total)
    data_sum["total_earning"] = str(earning_total)

    table.add_row(data_sum["total_days"],data_sum["total_hours"],data_sum["total_earning"],data_sum["rate_used"])
    console.print(table)


def pretty_table(*,records:List[Dict[str, Any]]) -> Table:

        def day_is(date_:str):
            from datetime import datetime
            from enum import Enum 

            class Weekday(Enum):
                Monday      = 0
                Tuesday     = 1
                Wednesday   = 2
                Thursday    = 3
                Friday      = 4
                Saturday    = 5
                Sunday      = 6

            assert type(date_) is str, f"{date_} must be a str date"

            try:
                date_obj = datetime.strptime(date_, desired_date_format)
                day_of_week = date_obj.weekday()
                return Weekday(day_of_week).name
            except ValueError:
                return ""     


        console = Console()
        table = Table(show_header=True, header_style="bold yellow")

        # Header
        table.add_column("Date", style="dim", width=12)
        table.add_column("Day")
        table.add_column("Time in")
        table.add_column("Time out")
        table.add_column("Worked (in hours)",justify="right")
        table.add_column("Earning (in £)",justify="right")

        for record in records:
            date_, time_in, time_out = record.get("date_"), record.get("time_in"), record.get("time_out")

            data = {
            "time_in":time_in,
            "time_out":time_out,
            "date_":date_,
            }

            # computations
            per_duration = time_difference(**data)
            earning = time_difference_in_earning(**data)
            
            # convert to str for table format
            earning_str = str(earning)
            per_dur_str  = str(per_duration)

            day_ = day_is(date_)
            table.add_row(date_, day_, time_in, time_out, per_dur_str, earning_str)
        console.print(table)


def main() -> None:

    try:
        file_path, rate = get_args_from_command(standalone_mode=False)
    except KeyboardInterrupt:
        logging.error("Operation interrupted while running")

    if not all([file_path,rate]):
        return

    if records := get_file_data(file_path):
        pretty_table(records = records)
        pretty_table_for_totals(records = records)


if __name__ == '__main__':
    main()