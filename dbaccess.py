import mysql.connector
import bottools
from botclasses import PostWrapper, PostStatsWrapper, SubscriberWrapper, CommentWrapper
from datetime import datetime

props = bottools.get_properties("dbaccess")

tables = {
    "POSTS" : {
        "name" : "posts",
        "id" : "id"
    },
    "POST_STATS" : {
        "name" : "post_stats",
        "id" : "post_id"
    },
    "SUBSCRIBERS" : {
        "name" : "subscribers",
        "id" : "post_id"
    },
    "COMMENTS" : {
        "name" : "comments",
        "id" : "id"
    }
}

class DbAccess:

    def __init__(self):
        self.cursor = None
        self.db = None

    def open_connection(self):

        # Connect to MySQL database
        self.db = mysql.connector.connect(host=props["db_credentials"]["host"],
                                          user=props["db_credentials"]["user"],
                                          passwd=props["db_credentials"]["passwd"],
                                          database=props["db_credentials"]["database"])
        self.cursor = self.db.cursor()

    def post_to_db(self, obj):
        if isinstance(obj, PostWrapper):
            self.insert_post(obj)
        elif isinstance(obj, PostStatsWrapper):
            self.insert_poststats(obj)
        elif isinstance(obj, SubscriberWrapper):
            self.insert_subscriber(obj)
        elif isinstance(obj, CommentWrapper):
            self.insert_comment(obj)

    # Add post to the database. If the post already exists, update if there's
    # info that wasn't there the first time.
    def insert_post(self, post):
        # if not self.exists_in_db(post._id, tables["POSTS"]):
        print("Add / Update posts %s ... %s --- %s" % (post._id, post.title, post.created_utc,))
        sql = "INSERT INTO %s " % tables["POSTS"]["name"]
        sql += ("(id, "
                "title, "
                "permalink, "
                "shortlink, "
                "url, "
                "author, "
                "timestamp, "
                "created_utc, "
                "type, "
                "subreddit) "
                "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                "ON DUPLICATE KEY UPDATE "
                "title = IFNULL (title, VALUES(title)), "
                "permalink = IFNULL (permalink, VALUES(permalink)), "
                "shortlink = IFNULL (shortlink, VALUES(shortlink)), "
                "url = IFNULL (url, VALUES(url)), "
                "timestamp = IFNULL (timestamp, VALUES(timestamp)), "
                "created_utc = IFNULL (created_utc, VALUES(created_utc)), "
                "type = IFNULL (type, VALUES(type)), "
                "subreddit = IFNULL (subreddit, VALUES(subreddit));")
        cols = (post._id,
                post.title,
                post.permalink,
                post.shortlink,
                post.url,
                post.author,
                post.timestamp,
                datetime.utcfromtimestamp(post.created_utc),
                post.type,
                post.subreddit)


        self.cursor.execute(sql, cols)

    def insert_poststats(self, pstats):
        pstats_update_sql = ("INSERT INTO %s " % (tables["POST_STATS"]["name"],))
        pstats_update_sql += ("(post_id, "
                              "score, "
                              "ups, "
                              "downs, "
                              "upvote_ratio, "
                              "view_count, "
                              "num_comments, "
                              "over_18, "
                              "archived, "
                              "link_flair_text) "
                              "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                              "ON DUPLICATE KEY UPDATE "
                              "score = VALUES(score), "
                              "ups = VALUES(ups), "
                              "downs = VALUES(downs), "
                              "upvote_ratio = VALUES(upvote_ratio), "
                              "view_count = VALUES(view_count), "
                              "num_comments = VALUES(num_comments), "
                              "over_18 = VALUES(over_18),"
                              "archived = VALUES(archived),"
                              "link_flair_text = VALUES(link_flair_text);")
        cols = (pstats.post_id,
                pstats.score,
                pstats.ups,
                pstats.downs,
                pstats.upvote_ratio,
                pstats.view_count,
                pstats.num_comments,
                pstats.over_18,
                pstats.archived,
                pstats.link_flair_text)

        print(" -- Add / Update post_stats %s ... " % pstats.post_id)
        self.cursor.execute(pstats_update_sql, cols)

    def insert_subscriber(self, subsc):
        if subsc.subcount is not None:
            sql = "INSERT IGNORE INTO %s (post_id, utc, subcount, subreddit) " % tables["SUBSCRIBERS"]["name"]
            sql += "VALUES(%s, %s, %s, %s);"
            cols = (subsc.post_id,
                    datetime.utcfromtimestamp(subsc.utc),
                    subsc.subcount,
                    str(subsc.subreddit), )

            print(" -- Add / Update subscribers %s ..." %
                    (subsc.post_id,))
            self.cursor.execute(sql, cols)


    def insert_comment(self, c):

        com_update_sql = ("INSERT INTO %s " % (tables["COMMENTS"]["name"],))
        com_update_sql += ("( id, "
                           "body, "
                           "parent_id, "
                           "submission, "
                           "link_id, "
                           "created_utc, "
                           "permalink, "
                           "score, "
                           "ups, "
                           "downs, "
                           "author ) "
                           "VALUES(%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) "
                           "ON DUPLICATE KEY UPDATE "
                           "score = VALUES(score), "
                           "ups = VALUES(ups), "
                           "downs = VALUES(downs);")
        cols = (c._id,
                str(c.body),
                c.parent_id,
                c.submission,
                c.link_id,
                datetime.utcfromtimestamp(c.created_utc),
                c.permalink,
                c.score,
                c.ups,
                c.downs,
                c.author,)

        print(" -- Add / Update comments %s ... " % c._id)
        self.cursor.execute(com_update_sql, cols)

    # Convenience method to determine if this object is represented in the database
    def exists_in_db(self, objId, table):
        query = ("SELECT %s FROM %s WHERE %s" % (table["id"], table["name"], table["id"]))
        self.cursor.execute(query + " = %s;", (objId,))
        result = self.cursor.fetchone()
        return True if result else False

    def queryAll(self, sql, cols):
        self.cursor.execute(sql, cols)
        return self.cursor.fetchall()

    def queryOne(self, sql, cols):
        self.cursor.execute(sql, cols)
        return self.cursor.fetchone()

    def close_cursor(self):
        self.cursor.close()

    def close_db(self):
        self.db.close()

    def commit_db(self):
        print("Executing database commit.")
        self.db.commit()

    def commit_and_close(self):
        self.close_cursor()
        self.commit_db()
        self.close_db()

    # Queries the database for the given id, and populates the object importObj with what is found and returns it.
    def get_from_db(self, objId, table, importObj):
        if objId:
            sql = "SELECT * FROM %s " % table["name"]
            sql += "WHERE id= %s"
            this_id = (objId,)
            self.cursor.execute(sql, this_id)
            result = self.cursor.fetchone()
            importObj.get_from_list(result)
        return importObj