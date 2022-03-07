from datetime import datetime, timedelta
from bottools import get_properties
import mysql.connector
import praw

datetime_now = datetime.utcnow()  # Current time
now_timestamp = datetime_now.timestamp()

props = get_properties("contest_scanner")
# log_file_name = props["log_path"] + "contest_scanner.log"  # Logfile filename
user_agent = "AnalogBot contest entry scanner v" + props["version"] + " by /u/jeffk42"

def post_submission_exists():
    print('User has already submitted an entry.')

def post_is_self():
    print('Post is a self post.')

def post_link_exists():
    print('This image has already been submitted.')

# Reddit OAuth
reddit = praw.Reddit(client_id=props["reddit_credentials"]["client_id"],
                     client_secret=props["reddit_credentials"]["client_secret"],
                     password=props["reddit_credentials"]["password"],
                     user_agent=user_agent,
                     username=props["reddit_credentials"]["username"])

# Logging
# logFile = open(log_file_name, 'a+')
# logFile.write('\n-=-=-=-=-=-=-=-=-=-=-=-=-=-\nScript start, ' + user_agent + '\n')
# logFile.write(str(datetime_now) + "\n")

subreddit = reddit.subreddit('analogbot')
for submission in subreddit.stream.submissions():
    if submission.link_flair_text == "Contest Submission":
        # Connect to MySQL database
        db = mysql.connector.connect(host=props["db_credentials"]["host"],
                                     user=props["db_credentials"]["user"],
                                     passwd=props["db_credentials"]["passwd"],
                                     database=props["db_credentials"]["database"])
        cursor = db.cursor()

        # check to see if the user has already submitted something
        query = ("SELECT * FROM contestentries WHERE username")
        cursor.execute(query + " = %s;", (submission.author.name,))
        result = cursor.fetchone()

        if result:
            post_submission_exists()
        elif submission.is_self:
            post_is_self()

        # check to see if the submission has already been submitted.
        query = ("SELECT * FROM contestentries WHERE url")
        cursor.execute(query + " = %s;", (submission.url,))
        result = cursor.fetchone()

        if result:
            post_link_exists()

        contest_id = 'test'
        
        # Submission is probably valid. Add to the database.
        sql = "INSERT INTO contestentries "
        sql += ("contestid, "
                "username, "
                "url, "
                "postid) "
                "VALUES(%s, %s, %s, %s);")
        cols = (contest_id,
                submission.author.name,
                submission.url,
                submission.id)

        cursor.execute(sql, cols)


        print(submission.title)