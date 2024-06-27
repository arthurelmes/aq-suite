import pprint
import time
from datetime import datetime

from sds011 import SDS011
from typing import Dict

def measure_pm() -> Dict:
    sensor = SDS011("/dev/ttyUSB0", use_query_mode=True)
    reading = sensor.query()
    return {"pm2.5": reading[0], "pm10": reading[1]}


def append_data_to_file(file_name: str, datum: str) -> None:
    with open(file_name, "a") as f:
        f.write(",".join([datetime.now().strftime("%Y-%m-%dT%H:%M:%S"), str(datum)]))
        f.write("\n")
        

if __name__ == "__main__":
    log_file_path = "/home/arthurelmes/Desktop/log_pm_test_0.txt"
    data = dict()
    for i in range(1000):
        timestamp = datetime.strftime(datetime.now(), "%Y%m%dT:%H:%M:%S.%f")
        measurements = measure_pm()
        data[timestamp] = measurements
        print(measurements)
        append_data_to_file(log_file_path, ",".join([str(measurements["pm2.5"]), str(measurements["pm10"])]))
        time.sleep(30)
        
    pprint.pprint(data)
