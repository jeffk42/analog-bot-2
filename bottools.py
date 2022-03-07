import json
from psutil import cpu_count
import platform
import datetime


# Uses the setup.json file to get the props path and build properties
# based on the script that's calling it.
def get_properties(script_name=None):
    result = {}
    file = "setup.json"
    with open(file, "r") as setup_file:
        result.update(json.load(setup_file))
    props_path = result["props_path"]
    files = [props_path + result["credentials_file"],
             props_path + "global-properties.json"]

    if script_name is not None:
        files.append(props_path + script_name + "-properties.json")

    for file in files:
        with open(file, "r") as infile:
            result.update(json.load(infile))

    return result


def get_date_range_from_week_num(year, calendar_week):
    # use .format() instead of f'---' because format strings aren't available yet in RPi version of python
    monday = datetime.datetime.strptime('{year}-{week}-1'.format(year=year, week=calendar_week), "%Y-%W-%w")
    return monday, monday + datetime.timedelta(days=7)

sysinfo_string_markdown = ("^(Executed on host) **^(" + platform.node() +
                           ")** ^(in %s) ^(| Python v" +
                           platform.python_version() + " " + platform.system() +
                           " " + str(cpu_count(logical=True)) + "x " + platform.machine() + ")")

sysinfo_string = ("Executed on host " + platform.node() + " in %s | Python v" +
                           platform.python_version() + " " + platform.system() +
                           " " + str(cpu_count(logical=True)) + "x " + platform.machine())

