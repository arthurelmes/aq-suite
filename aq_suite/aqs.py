import pprint
import time
from datetime import datetime
from datetime import timedelta

from sds011 import SDS011
from typing import Dict

import argparse
import logging
import pprint
import time
from datetime import datetime, timedelta
from typing import Dict
import os.path as op
import mh_z19 as m19

FILL_VALUE = -999.0

logging.basicConfig(
    level=logging.DEBUG,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger(__name__)


def parse_args() -> Dict:
    parser = argparse.ArgumentParser(
        prog="log_c02",
        description="Log CO2 concentration at given interval for given time period.",
    )
    parser.add_argument(
        "-l",
        "--log_dir_path",
        type=str,
        help="[Required] Full path to output dir for logfiles.",
        required=True
    )
    parser.add_argument(
        "-p",
        "--ping_interval",
        type=int,
        help="[Optional] Number of seconds between sensor reads.",
        default=30,
    )
    parser.add_argument(
        "-n",
        "--notes",
        type=str,
        help="[Optional] Notes for future refernce, printed in each logfile's header.",
        default="",
    )
    parser.add_argument(
        "-sd",
        "--start_delay_hours",
        type=float,
        help="[Optional] Delay in fractional hours before starting to log. Defaults to 0.",
        default=0.0,
    )
    parser.add_argument(
        "-lg",
        "--logging_time_hours",
        type=float,
        help="[Optional] Time in fractional hours to continue logging for. Defaults to 1.0",
        default=1.0,
    )

    args = parser.parse_args()
    args = vars(args)

    return args


def mesure_co2_temp() -> Dict:
    raw_reading = m19.read()
    co2_temp = {"co2": raw_reading.get("co2", FILL_VALUE)), "temp_c": raw_reading["temp"]}
    return co2_temp


def measure_pm() -> Dict:
    sensor = SDS011("/dev/ttyUSB0", use_query_mode=True)
    reading = sensor.query()
    pm = dict()
    for pm_val in ("pm2.5", 0), ("pm10", 1)):
        try:
            pm[pm_val[0]] = reading[pm_val[1]]
        except IndexError:
            pm[pm_val[0]] = FILL_VALUE
            
    return pm

def append_data_to_file(file_name: str, datum: str) -> None:
    with open(file_name, "a") as f:
        f.write(",".join([datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), str(datum)]))
        f.write("\n")

        
def add_note_header(file_path: str, notes: str) -> None:
    """Create log file header, including any user-specified notes."""
    with open(file_path, "w") as f:
        f.write(notes)
        f.write("\n\n")

         
if __name__ == "__main__":
    args = parse_args()

    formatted_time = datetime.strftime(datetime.now(), '%Y%m%dT%H%M%S')
    co2_log_file_path = op.join(args["log_dir_path"], f"co2-log-{formatted_time}.txt")
    pm_log_file_path = op.join(args["log_dir_path"], f"pm-log-{formatted_time}.txt")
    half_sleep_secs = int(args["ping_interval"]/2)

    add_note_header(co2_log_file_path, args["notes"])
    add_note_header(pm_log_file_path, args["notes"])

    args["start_datetime"] = datetime.now() + timedelta(hours=args["start_delay_hours"])
    args["end_datetime"] = args["start_datetime"] + timedelta(hours=args["logging_time_hours"])

    pretty_args = pprint.pformat(args)
    logger.info("Running with the following configuration:\n%s", pretty_args)
    while datetime.now() < args["end_datetime"]:
        if args["start_datetime"] <= datetime.now():
            co2_datum = measure_co2_temp()
            logger.debug("CO2 concentration: %f", co2_datum["co2"])
            append_data_to_file(co2_log_file_path, ",".join([str(co2_datum["co2"]), str(co2_datum["temp_c"])])
            time.sleep(half_sleep_secs)

            pm_datum = measure_pm()
            append_data_to_file(pm_log_file_path, ",".join([str(pm_datum["pm2.5"]), str(pm_datum["pm10"])]))
            logger.debug("PM2.5 concentration: %f, PM10 concentration: %f", pm_datum["pm2.5"], pm_datum["pm10"])
            time.sleep(half_sleep_secs)

        else:
            time.sleep(60)
