from dateutil.relativedelta import relativedelta
from datetime import datetime
import praw

def get_subreddit_info(subreddit, endofweek, creds):
    var_list = {};
    reddit = praw.Reddit(client_id=creds["client_id"], client_secret=creds["client_secret"],
                         password=creds["password"],
                         user_agent="AnalogBot Subreddit Info Generator by /u/jeffk42",
                         username=creds["username"])
    sub = reddit.subreddit(subreddit)
    created = datetime.fromtimestamp(sub.created_utc)

    var_list["subreddit_created"] = created.strftime("%A %B %d, %Y %H:%M:%S")

    age = relativedelta(endofweek, created)
    var_list["subreddit_age"] = ("%s Years, %s Months, %s Days, %s Hours, %s Minutes" %
                                       (age.years, age.months, age.days, age.hours, age.minutes))

    var_list["subscribers"] = sub.subscribers

    return var_list

def get_last_week_info(subreddit, endofweek, creds):
    pass

# If two parameters, the percentage string is created from num / denom. If one parameter,
# the percentage is assumed to be correct already and "%" is added.
def get_percentage(num, denom=None):
    if denom is not None and denom > 0:
        return "{0:.2%}".format(num / denom)
    else:
        ans = 100 * float(num)
        return  str(ans) + "%"

# Convenience methods for use in the query definition
def util_perc(varlist, name_num, name_denom=None):
    if isinstance(name_num, str):
        if isinstance(name_denom, str):
            return get_percentage(varlist[name_num], varlist[name_denom] if name_denom is not None else None)
        else:
            return get_percentage(varlist[name_num],
                                  name_denom if name_denom is not None else None)
    else:
        if isinstance(name_denom, str):
            return get_percentage(name_num, varlist[name_denom] if name_denom is not None else None)
        else:
            return get_percentage(name_num, name_denom if name_denom is not None else None)


def util_subtract(varlist, num1, num2):
    return (varlist[num1] - varlist[num2])