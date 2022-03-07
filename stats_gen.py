from bottools import get_properties, sysinfo_string_markdown, get_date_range_from_week_num
import sys
from datetime import timedelta, datetime
from dbaccess import DbAccess
import decimal
from stats_utils import get_subreddit_info, util_subtract, util_perc

datetime_now = datetime.utcnow()  # Current time
now_timestamp = datetime_now.timestamp()
year = datetime_now.strftime("%Y")
week = datetime_now.strftime("%W")
month = datetime_now.strftime("%m")
week_ago = datetime_now - timedelta(days=7)
now_string = datetime_now.strftime("%A %B %d, %Y %H:%M:%S %Z")
week_ago_string = week_ago.strftime("%A %B %d, %Y %H:%M:%S %Z")

props = get_properties("stats_gen")
log_file_name = props["log_path"] + "AnalogBotStatsGen-" + year + month + ".log"  # Logfile filename
user_agent = "AnalogBot Stats Generator v" + props["version"] + " by jeffk42"

# Get command line parameters if they exist
param_len = len(sys.argv)

if param_len > 1:
    year = int(sys.argv[1])
    week = int(sys.argv[2]) - 1

date_range = get_date_range_from_week_num(year, week) #[week_ago, datetime_now]
date_range_start_str = date_range[0].strftime("%A %B %d, %Y %H:%M:%S %Z")
date_range_finish_str = date_range[1].strftime("%A %B %d, %Y %H:%M:%S %Z")
date_range_first_week = get_date_range_from_week_num(year, 1)


# Open output file
outfile = open(props["log_path"] + (props["outfile_name"] % (year,week)), 'w')

query_var_list = {
    'start_date' : date_range[0],
    'end_date' : date_range[1],
    'first_week_start_date' : date_range_first_week[0],
    'first_week_end_date' : date_range_first_week[1],
    'weekly_aa_name' : props["weekly_aa_name"] % format(week, '02') # "'" + (props["weekly_aa_name"] % week).replace("'", r"\'") + "'"
    }

def perc(name_num, name_denom=None):
    return util_perc(query_var_list, name_num, name_denom)

def subtract(num1, num2):
    return util_subtract(query_var_list, num1, num2)

def time(val):
    return val.strftime("%d %b %Y %H:%M:%S UTC")

# Escape the characters that would break markdown links
def fix_link_title(title):
    return title.replace("[", r"\[").replace("]", r"\]")


# Builds the query and sets the result based on the definition provided in the properties file.
# This method is used for single numerical results like counts, averages, etc.
def get_query_stats(_chosen_stats):
    # Get a list of the available statistics in the provided section
    for key, value in sorted(_chosen_stats.items()):
        # Gets a list of the queries used in the statistic
        q_list = [ v for k,v in sorted(value.items()) if k.startswith('query')]
        for q in q_list:
            # for each query, look for the list of "query_vars", a pipe-delimited string. If the
            # string exists, create a tuple from it to pass into the query. If it doesn't exist,
            # default to just use start_time and end_time since every query requires at least that much.
            if 'query_vars' in q:
                varlist = q["query_vars"].split("|")
                varary = []
                for thevar in varlist:
                    varary.append(query_var_list[thevar])
                vars = tuple(varary)
            else:
                vars = (date_range[0], date_range[1],)

            if "type" in value and value["type"] == "post":
                # execute the query
                result = db.queryOne(q["query"], vars)

                # Truncate decimals and floats to two decimal places
                for result_val in result:
                    if isinstance(result_val, (decimal.Decimal, float,)) and result_val % 1 != 0:
                        result_val = "{0:.2f}".format(result_val)

                # Store the result in the dictionary under the name specified in "store_result".
                query_var_list[q["store_result"]] = result
            else:
                result_set = db.queryOne(q["query"], vars)
                result_val = 0
                if result_set is not None:
                    result_val = result_set[0]

                # Truncate decimals and floats to two decimal places
                if isinstance(result_val, (decimal.Decimal, float,)) and result_val % 1 != 0:
                    result_val = "{0:.2f}".format(result_val)

                # Store the result in the dictionary under the name specified in "store_result".
                query_var_list[q["store_result"]] = result_val


# Output the result in a format defined by the properties file.
def output_query_stats(_chosen_stats):
    for a_key in sorted(_chosen_stats.keys()):
        if "output_vars" in _chosen_stats[a_key]:
            # Get the pipe-delimited string corresponding to the "%s" fields in the output string.
            varlist = _chosen_stats[a_key]["output_vars"].split("|")
            varary = []
            for thevar in varlist:
                # if one of the following characters exists in the field, treat it as a method call.
                # Otherwise, it's a key name for the dictionary.
                nonvar_chars = r'(),'
                multivar_chars = r'\.'
                if any(elem in thevar for elem in nonvar_chars):
                    varary.append(eval(thevar.strip()))
                elif any(elem in thevar for elem in multivar_chars):
                    thevars = thevar.split(".")

                    formatted_var = (query_var_list[thevars[0].strip()][int(thevars[1].strip())])
                    if isinstance(formatted_var, datetime):
                        formatted_var = time(formatted_var)
                    varary.append(formatted_var)
                else:
                    varary.append(query_var_list[thevar.strip()])

            vars = tuple(varary)
            output("* " + _chosen_stats[a_key]["output_str"] % vars)


def generate_stats(chosen_stats):
    get_query_stats(chosen_stats)
    output_query_stats(chosen_stats)

def generate_single_stat(stat):
    wrapper = {
        "wrap_single" : stat
    }
    generate_stats(wrapper)


def new_section(title):
    output("")
    output("## **%s** ##" % (title))
    output("")

def output(str):
    print(str)
    outfile.write(str + "\n")






# Main

# Generate stats for /r/analog

output("# **Weekly Statistics For /r/Analog, Week %s** #" % (week,))
output("")
output("_From **%sUTC** to **%sUTC**_" % (date_range_start_str, date_range_finish_str))

# Get cursor
db = DbAccess()
db.open_connection()

query_var_list.update(get_subreddit_info('analog', date_range[1], props["reddit_credentials"]))

new_section("Subreddit Information")
output("* Subreddit Created On: **%s**" % query_var_list["subreddit_created"])
output("* Subreddit Age (End of Week): **%s**" % query_var_list["subreddit_age"])
output("* Number of Subscribers (End of Week): **%s**" % query_var_list["subscribers"])
generate_stats(props["subreddit_data"])


# The basic stats can be generated using the convenience methods above, but when
# things get a little weird, we need to do them separately so they can be formatted
# as needed.

new_section("Post Statistics")

# Get total posts first, so the other stats can use it for percentage calculation
generate_stats(props["prelim_stats_data"])
# Print image post/text post statistics
generate_stats(props["sum_stats_data"])

# Print Upvote and Comment Statistics
new_section("Vote/Comment Statistics")
generate_stats(props["vote_comment_data"])
generate_stats(props["user_stats_data"])

# Generate and print the photo detail statistics
new_section("Film Statistics")
generate_stats(props["photo_film_stats_data"])

# Generate and print the camera detail statistics
new_section("Camera Statistics")
generate_stats(props["photo_camera_stats_data"])

# Generate and print the random statistics
new_section("Random Statistics and Myth Busters")
generate_stats(props["random_stats"])


# Statsgen metadata
exec_time = datetime.utcnow().timestamp()
delta = timedelta(seconds=(exec_time - now_timestamp))
output("")
output("&#x200B;\n\n&#x200B;")
output("")
output("**^(" + user_agent + ")** ^(|) ")
output(sysinfo_string_markdown % (str(delta.total_seconds()) + " seconds"))
output("")
output("^(Bug report or suggestion for new stats or functionality?) [^(Visit the Issues page)](https://bitbucket.org/jeffk42/analog-bot/issues?status=new&status=open).")

outfile.flush()
outfile.close()
db.close_cursor()
db.close_db()
