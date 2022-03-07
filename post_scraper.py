from botclasses import PostWrapper, PostStatsWrapper, SubscriberWrapper, CommentWrapper
from bottools import get_properties
from datetime import datetime, timedelta
import praw
from bottools import sysinfo_string
from dbaccess import DbAccess
import rpi_func as pi
import time



pi.setup_feedback_lights()
pi.light_off(pi.all_lights)
pi.light_solid(pi.lights['blue_1'])

num_submissions = 1000
datetime_now = datetime.utcnow()  # Current time
now_timestamp = datetime_now.timestamp()
year = datetime_now.strftime("%Y")  # Current year
month = datetime_now.strftime("%m")  # Current month
dayOfWeek = datetime_now.strftime("%A")  # Current day of the week
hourOfDay = datetime_now.strftime("%H")  # Current hour

props = get_properties("post_scraper")
log_file_name = props["log_path"] + "R2MySQL-" + year + month + ".log"  # Logfile filename
user_agent = "AnalogBot metadata saver v" + props["version"] + " by /u/jeffk42"


def update_progress_lights(perc):
    if 0 <= perc < 20 and not pi.get_light_status(pi.lights["progress_1"]):
        pi.light_solid(pi.lights['progress_1'])
    elif 20 <= perc < 40 and not pi.get_light_status(pi.lights["progress_2"]):
        pi.light_solid(pi.lights['progress_2'])
    elif 40 <= perc < 60 and not pi.get_light_status(pi.lights["progress_3"]):
        pi.light_solid(pi.lights['progress_3'])
    elif 60 <= perc < 80 and not pi.get_light_status(pi.lights["progress_4"]):
        pi.light_solid(pi.lights['progress_4'])
    elif perc >= 80 and not pi.get_light_status(pi.lights["progress_5"]):
        pi.light_solid(pi.lights['progress_5'])


# Main

db = DbAccess()
db.open_connection()

# Reddit OAuth
reddit = praw.Reddit(client_id=props["reddit_credentials"]["client_id"],
                     client_secret=props["reddit_credentials"]["client_secret"],
                     password=props["reddit_credentials"]["password"],
                     user_agent=user_agent,
                     username=props["reddit_credentials"]["username"])

# Logging
logFile = open(log_file_name, 'a+')
logFile.write('\n-=-=-=-=-=-=-=-=-=-=-=-=-=-\nScript start, ' + user_agent + '\n')
logFile.write(str(datetime_now) + "\n")

subcount = 0

# Iterate through subreddits to get post info from each
for sub in props["subreddits"]:

    pi.light_off([pi.lights['progress_1'],
                  pi.lights['progress_2'],
                  pi.lights['progress_3'],
                  pi.lights['progress_4'],
                  pi.lights['progress_5']])
    
    subcount += 1
    itercount = 0
    pi.light_solid(pi.lights['progress_g'+str(subcount)])

    logFile.write("Pulling posts from " + sub + "\n")

    # Get latest submissions from Reddit
    praw_submissions = reddit.subreddit(sub).new(limit=num_submissions)

    for praw_submission in praw_submissions:
        pi.light_solid(pi.lights["yellow_1"])
        itercount += 1
        update_progress_lights((itercount / num_submissions) * 100)

        print(" ---- un-lazy this submission: %s %s" % (praw_submission.id, praw_submission.shortlink,))

        # Submissions
        submission = PostWrapper()
        submission.get_from_submission(praw_submission)
        db.post_to_db(submission)

        # Post Stats
        pstats = PostStatsWrapper()
        pstats.get_from_submission(praw_submission)
        db.post_to_db(pstats)

        # Subscriber Count
        subsc = SubscriberWrapper()
        subsc.get_from_submission(praw_submission)
        db.post_to_db(subsc)


        # Comments
        comment = CommentWrapper()
        praw_submission.comments.replace_more(limit=None)
        for praw_comment in praw_submission.comments.list():
            comment.get_from_comment(praw_comment)
            db.post_to_db(comment)

        pi.light_off(pi.lights['yellow_1'])

        if (itercount % 100) == 0:
            db.commit_db()



# Clean up connections
db.commit_and_close()


# Statsgen metadata
exec_time = datetime.utcnow().timestamp()
delta = timedelta(seconds=(exec_time - now_timestamp))
logFile.write(sysinfo_string % (str(delta.total_seconds()) + " seconds"))
print(sysinfo_string % (str(delta.total_seconds()) + " seconds"))

logFile.close()
pi.teardown_feedback_light()
