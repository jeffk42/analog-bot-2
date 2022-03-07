import json
import urllib.request
from botclasses import PostWrapper, PostStatsWrapper
from datetime import datetime, timedelta
import mysql.connector
import time
from pprint import pprint

# Render the title string safe
# def fix_title(title):  # Remove unsafe characters from the title
#     temp = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore')
#     temp = str(temp)
#     temp_len = len(temp)
#     temp = temp[2:temp_len - 1]
#     return temp

def get_properties():

    props_path = "../properties/"
    files = [props_path + "credentials.json",
             props_path + "global-properties.json"]
    result = {}
    for file in files:
        with open(file, "rb") as infile:
            result.update(json.load(infile))

    return result


# Convenience method to determine if this object is represented in the database
def exists_in_db(table, column, idstr, _cursor):
    sql = "SELECT %s FROM %s WHERE %s = " % (column, table, column,)
    _cursor.execute(sql+"%s;",(idstr,))
    result = _cursor.fetchone()
    return True if result else False


datetime_now = datetime.utcnow()  # Current time
now_timestamp = datetime_now.timestamp()
# begin_time = 1325376000 probably near the beginning of the subreddit
end_time = 1540074000
end_next = end_time
delta = 250000
begin_time = 1519862400
begin_next = end_time
begin_next -= delta

props = get_properties()
url = "https://api.pushshift.io/reddit/search/submission/?"
static_params = "&subreddit=analog&size=1000&fields=id,title,permalink,url,author,created_utc,is_self,subreddit,score,num_comments,over_18,subreddit_subscribers"
# Connect to MySQL database
db = mysql.connector.connect(host=props["db_credentials"]["host"],
                             user=props["db_credentials"]["user"],
                             passwd=props["db_credentials"]["passwd"],
                             database=props["db_credentials"]["database"])
cursor = db.cursor()
while begin_next >= (begin_time - delta):
    timeframe = "before="+str(end_next)+"&after="+str(begin_next)
    print(timeframe)

    req = urllib.request.Request(url + timeframe + static_params)
    opener = urllib.request.build_opener()
    f = opener.open(req)
    sub_json = json.loads(f.read())
    data = sub_json["data"]

    for entry in data:
        print(entry["id"])

        entry["type"] = "selfpost" if entry["is_self"] else "link"
        self = PostWrapper(None, (entry["id"],
                              entry["title"],
                              entry["permalink"],
                              None,
                              entry["url"],
                              entry["author"],
                              None,
                              entry["created_utc"],
                              entry["type"],
                              entry["subreddit"]))

        if not exists_in_db("posts", "id", entry["id"], cursor):
            print("Inserting post with id %s into database." % self._id)
            sql = ("INSERT INTO posts (id, title, permalink, shortlink, url, author, timestamp, created_utc, type, subreddit) "
                "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s);")

            cols = (self._id, self.title, self.permalink, self.shortlink, self.url, self.author, self.timestamp,
                datetime.utcfromtimestamp(self.created_utc), self.type, self.subreddit)

            cursor.execute(sql, cols)

        sql = ("INSERT INTO post_stats (post_id, score, ups, downs, num_comments, over_18) "
           "VALUES(%s, %s, %s, %s, %s, %s) ON DUPLICATE KEY UPDATE score = VALUES(score),"
           "ups = VALUES(ups), downs = VALUES(downs), num_comments = VALUES(num_comments), over_18 = VALUES(over_18);")
        cols = (entry["id"], entry["score"], None, None, entry["num_comments"], entry["over_18"])

        print("add/update id:%s score:%s comments:%s, over_18:%s" % (
            entry["id"], entry["score"], entry["num_comments"], entry["over_18"],))
        cursor.execute(sql, cols)

        # subscriber count
        if not exists_in_db("subscribers", "post_id", entry["id"], cursor):
            if "subreddit_subscribers" in entry and entry["id"] is not None and entry["created_utc"] is not None and entry["subreddit_subscribers"] is not None:
                sql = ("INSERT INTO subscribers (post_id, utc, subcount, subreddit) "
                    "VALUES(%s, %s, %s);")
                cols = (entry["id"], datetime.utcfromtimestamp(entry["created_utc"]), entry["subreddit_subscribers"],
                        entry["subreddit"])


                print("add/update id:%s utc:%s subcount:%s" % (
                    entry["id"], entry["created_utc"], entry["subreddit_subscribers"],))
                cursor.execute(sql, cols)

    print("Completed pass back to " + str(begin_next))
    db.commit()
    begin_next -= delta
    end_next -= delta
    time.sleep(1.0)

cursor.close()
db.commit()
db.close()
exec_time = datetime.utcnow().timestamp()
delta = timedelta(seconds=(exec_time - now_timestamp))
print("Execution time: " + str(delta.microseconds / 1000000) + " seconds")
