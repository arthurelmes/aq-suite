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
from typing import Dict, List
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


def measure_co2_temp() -> Dict:
    raw_reading = m19.read_all()
    co2_temp = {"co2": raw_reading.get("co2", FILL_VALUE), "temp_c": raw_reading.get("temperature", FILL_VALUE)}
    return co2_temp


def measure_pm() -> Dict:
    sensor = SDS011("/dev/ttyUSB0", use_query_mode=True)
    reading = sensor.query()
    pm = dict()
    for pm_val in (("pm2.5", 0), ("pm10", 1)):
        try:
            pm[pm_val[0]] = reading[pm_val[1]]
        except IndexError:
            pm[pm_val[0]] = FILL_VALUE

    return pm


def append_data_to_file(file_name: str, datum: str, usecols: List) -> None:
    write_cols = [datum["measurement_time"].strftime("%Y-%m-%dT%H:%M:%S")]
    write_cols += [str(datum[i]) for i in usecols if i != "measurement_time"]
    write_cols = ",".join(write_cols)
    with open(file_name, "a") as f:
        f.write(write_cols)
        f.write("\n")


def add_log_file_cols(file_path: str, cols: List) -> None:
    """Create log file header, including any user-specified notes."""
    with open(file_path, "w") as f:
        f.write(",".join(cols))
        f.write("\n")


if __name__ == "__main__":
    args = parse_args()

    formatted_time = datetime.strftime(datetime.now(), '%Y%m%dT%H%M%S')

    note_str = args.get("notes", "").replace(" ", "-")
    log_file_path = op.join(args["log_dir_path"], note_str, f"co2-pm-log-{formatted_time}.txt")
    half_sleep_secs = int(args["ping_interval"]/2)
    data_cols = ["measurement_time", "co2", "temp_c", "pm2.5", "pm10"]

    args["start_datetime"] = datetime.now() + timedelta(hours=args["start_delay_hours"])
    args["end_datetime"] = args["start_datetime"] + timedelta(hours=args["logging_time_hours"])

    pretty_args = pprint.pformat(args)
    logger.info("Running with the following configuration:\n%s", pretty_args)
    add_log_file_cols(log_file_path, cols=data_cols)

    while datetime.now() < args["end_datetime"]:
        if args["start_datetime"] <= datetime.now():
            co2_pm_datum = measure_co2_temp()
            logger.debug("\nCO2 concentration (PPM): %f\nTemperature (C) %f", co2_pm_datum["co2"], co2_pm_datum["temp_c"])
            time.sleep(half_sleep_secs)

            co2_pm_datum.update(measure_pm())
            co2_pm_datum["measurement_time"] = datetime.now()
            logger.debug("\nPM2.5 concentration: %f\nPM10 concentration: %f\n", co2_pm_datum["pm2.5"], co2_pm_datum["pm10"])

            append_data_to_file(log_file_path, co2_pm_datum, data_cols)
            time.sleep(half_sleep_secs)

        else:
            time.sleep(60)
