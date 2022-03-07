import praw
import json
import mysql.connector
import pprint
from datetime import timedelta, datetime

def get_properties():

    props_path = "../properties/"
    files = [props_path + "credentials.json",
             props_path + "global-properties.json"]
    result = {}
    for file in files:
        with open(file, "rb") as infile:
            result.update(json.load(infile))

    return result

datetime_now = datetime.utcnow()  # Current time
now_timestamp = datetime_now.timestamp()


props = get_properties()
user_agent = "AnalogBot Stats Generator by /u/jeffk42"
# Connect to MySQL database
db = mysql.connector.connect(host=props["db_credentials"]["host"],
                             user=props["db_credentials"]["user"],
                             passwd=props["db_credentials"]["passwd"],
                             database=props["db_credentials"]["database"])

# Reddit OAuth
reddit = praw.Reddit(client_id=props["reddit_credentials"]["client_id"],
                     client_secret=props["reddit_credentials"]["client_secret"],
                     password=props["reddit_credentials"]["password"],
                     user_agent=user_agent,
                     username=props["reddit_credentials"]["username"])

cursor = db.cursor()

cursor.execute("select id from posts limit 10;")

id_list = cursor.fetchall()
sql = ("INSERT INTO post_stats (id, ups, downs, num_comments, over_18) "
       "VALUES(%s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE "
       "ups = VALUES(ups), downs = VALUES(downs), num_comments = VALUES(num_comments), over_18 = VALUES(over_18);")

for _id in id_list:
    this_id = _id[0]
    sub = reddit.submission(id=this_id)
    print("add/update id:%s ups:%s downs:%s comments:%s, over_18:%s" % (
    this_id, sub.ups, sub.downs, sub.num_comments, sub.over_18,))
    pprint.pprint(vars(sub))
    cols = (this_id, sub.ups, sub.downs, sub.num_comments, sub.over_18,)
    cursor.execute(sql, cols)
cursor.close()
db.commit()
db.close()

exec_time = datetime.utcnow().timestamp()
delta = timedelta(seconds=(exec_time - now_timestamp))
print("Execution time: " + str(delta.microseconds / 1_000_000) + " seconds")