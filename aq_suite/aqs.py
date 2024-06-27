import pprint
import time
from datetime import datetime

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
        "-p",
        "--ping_interval",
        type=int,
        help="Number of seconds between sensor reads.",
        default=30,
    )
    parser.add_argument(
        "-t0",
        "--start_datetime",
        type=lambda date_str: datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f"),
        help="Date in YYYY-MM-DDTHH:MM:SS.ffffff format. Defaults to current time.",
        default=datetime.now(),
    )
    parser.add_argument(
        "-t1",
        "--end_datetime",
        type=lambda date_str: datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f"),
        help="Date in YYYY-MM-DDTHH:MM:SS.ffffff format. Defaults to one hour from current time.",
        default=datetime.now() + timedelta(hours=1),
    )
    parser.add_argument(
        "-l",
        "--log_dir_path",
        type=str,
        help="Full path to output dir for logfiles.",
        default=f"/tmp/aqs/",
    )

    args = parser.parse_args()
    args = vars(args)

    return args


def measure_pm() -> Dict:
    sensor = SDS011("/dev/ttyUSB0", use_query_mode=True)
    reading = sensor.query()
    return {"pm2.5": reading[0], "pm10": reading[1]}


def append_data_to_file(file_name: str, datum: str) -> None:
    with open(file_name, "a") as f:
        f.write(",".join([datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), str(datum)]))
        f.write("\n")

        
if __name__ == "__main__":
    args = parse_args()
    pretty_args = pprint.pformat(args)

    formatted_time = datetime.strftime(datetime.now(), '%Y%m%dT%H%M%S')
    co2_log_file_path = op.join(args["log_dir_path"], f"co2-log-{formatted_time}.txt")
    pm_log_file_path = op.join(args["log_dir_path"], f"pm-log-{formatted_time}.txt")
    
    logger.info("Running with the following configuration:\n%s", pretty_args)
    while datetime.now() < args["end_datetime"]:
        if args["start_datetime"] <= datetime.now():
            co2_datum = m19.read()
            pm_datum = measure_pm()

            append_data_to_file(co2_log_file_path, co2_datum.get("co2", ""))
            append_data_to_file(pm_log_file_path, ",".join([str(pm_datum["pm2.5"]), str(pm_datum["pm10"])]))

            time.sleep(args["ping_interval"])
        else:
            time.sleep(60)
