import matplotlib.pyplot as plt
import matplotlib as mpl
import pandas as pd
import os.path as op
from matplotlib.dates import DateFormatter, AutoDateLocator

TEMP_INPUT = "/Users/arthurelmes/data/aq-suite/co2-pm-log-20250105T153240.txt"


def main():
    data = pd.read_csv(TEMP_INPUT, parse_dates=["measurement_time"])

    # Change default font size for tick labels
    mpl.rcParams['xtick.labelsize'] = 6  # Reduce font size for x-axis ticks
    mpl.rcParams['ytick.labelsize'] = 8  # Optionally for y-axis ticks

    fig, axes = plt.subplots(4)
    locator = AutoDateLocator()
    formatter = DateFormatter("%Y-%m-%d %H:%M:%S")

    for axis, var in zip(axes, ["co2", "temp_c", "pm2.5", "pm10"]):
        axis.plot(data.measurement_time, data[var])
        axis.set_xlabel("datetime")
        axis.set_ylabel(var)
        axis.xaxis.set_major_locator(locator)
        axis.xaxis.set_major_formatter(formatter)

    # ax_0.plot(data.measurement_time, data.co2)
    # ax_0.set_xlabel("datetime")
    # ax_0.set_ylabel("CO2 (PPM)")
    # ax_0.xaxis.set_major_locator(locator)
    # ax_0.xaxis.set_major_formatter(formatter)

    # ax_1.plot(data.measurement_time, data.temp_c)
    # ax_1.set_xlabel("datetime")
    # ax_1.set_ylabel("Temp (C)")
    # ax_1.xaxis.set_major_locator(locator)
    # ax_1.xaxis.set_major_formatter(formatter)


    out_plot_path = op.join(op.dirname(TEMP_INPUT), op.basename(TEMP_INPUT).replace(".txt", "_plot.pdf"))

    fig.autofmt_xdate()
    plt.savefig(out_plot_path)

if __name__ == "__main__":
    main()
