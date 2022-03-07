from bottools import get_properties, get_date_range_from_week_num
from datetime import datetime, timedelta
import praw
import sys

props = get_properties("stats_gen")
# log_file_name = props["log_path"] + "R2MySQL-" + year + month + ".log"  # Logfile filename
user_agent = "AnalogBot weekly stats posting script v" + props["version"] + " by /u/jeffk42"

reddit = praw.Reddit(client_id=props["reddit_credentials"]["client_id"],
                     client_secret=props["reddit_credentials"]["client_secret"],
                     password=props["reddit_credentials"]["password"],
                     user_agent=user_agent,
                     username=props["reddit_credentials"]["username"])

flair_id = "728e7380-e57d-11e2-8979-12313d05241f"

# Get command line parameters if they exist
param_len = len(sys.argv)

datetime_now = datetime.utcnow()  # Current time
year = int(datetime_now.strftime("%Y"))
week = int(datetime_now.strftime("%W"))

if param_len > 1:
    year = int(sys.argv[1])
    week = int(sys.argv[2]) - 1

dates = get_date_range_from_week_num(year, week)
title_string = (dates[1] - timedelta(days=1)).strftime("%d %b %Y")

post_title = "Weekly Stats For /r/Analog, Week Ending %s" % title_string

with open(props["log_path"] + (props["outfile_name"] % (year, week)), 'r') as infile:
    content = infile.read()

sub = reddit.subreddit("Analog")

submission = sub.submit(title=post_title, selftext=content, flair_id=flair_id)
submission.mod.distinguish(how='yes', sticky=True)
submission.mod.sticky(True, True)

# for flair in reddit.subreddit('Analog').flair.link_templates:
#         print(flair)
