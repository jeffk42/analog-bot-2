import unicodedata


# Represents one submission entry in the database
class PostWrapper:
    def __init__(self):
        self._id = None
        self.title = None
        self.permalink = None
        self.shortlink = None
        self.url = None
        self.author = None
        self.timestamp = None
        self.created_utc = None
        self.type = None
        self.subreddit = None

    # Populate the object from a list of data
    def get_from_list(self, params):
        self._id = params[post_field["id"]]
        self.title = fix_title(params[post_field["title"]])
        self.permalink = fix_title(params[post_field["permalink"]])
        self.shortlink = params[post_field["shortlink"]]
        self.url = params[post_field["url"]]
        self.author = params[post_field["author"]]
        self.timestamp = params[post_field["timestamp"]]
        self.created_utc = params[post_field["created_utc"]]
        self.type = params[post_field["type"]]
        self.subreddit = params[post_field["subreddit"]]

    # Convert the PRAW Submission to this PostWrapper
    def get_from_submission(self, sub):
        self.get_from_list((str(sub.id),
                            str(sub.title),
                            str(sub.permalink),
                            str(sub.shortlink),
                            str(sub.url),
                            str(sub.author),
                            sub.created,
                            sub.created_utc,
                            "selfpost" if sub.is_self else "link",
                            str(sub.subreddit)
                            ))


# Render the title string safe
def fix_title(title):  # Remove unsafe characters from the title
    temp = unicodedata.normalize('NFKD', title).encode('ascii', 'ignore')
    temp = str(temp)
    temp_len = len(temp)
    temp = temp[2:temp_len - 1]
    return temp


class PostStatsWrapper:
    def __init__(self, post_id=None):
        self.post_id = post_id
        self.score = None
        self.ups = None
        self.downs = None
        self.upvote_ratio = None
        self.view_count = None
        self.num_comments = None
        self.over_18 = False
        self.archived = False
        self.link_flair_text = None

    def get_from_submission(self, sub):
        self.get_from_list((str(sub.id),
                            sub.score,
                            sub.ups,
                            sub.downs,
                            sub.upvote_ratio,
                            sub.view_count,
                            sub.num_comments,
                            sub.over_18,
                            sub.archived,
                            sub.link_flair_text
                            ))

    # Populate the object from a list of data
    def get_from_list(self, params):
        self.post_id = params[post_stats_field["post_id"]]
        self.score = params[post_stats_field["score"]]
        self.ups = params[post_stats_field["ups"]]
        self.downs = params[post_stats_field["downs"]]
        self.upvote_ratio = params[post_stats_field["upvote_ratio"]]
        self.view_count = params[post_stats_field["view_count"]]
        self.num_comments = params[post_stats_field["num_comments"]]
        self.over_18 = params[post_stats_field["over_18"]]
        self.archived = params[post_stats_field["archived"]]
        self.link_flair_text = params[post_stats_field["link_flair_text"]]


class SubscriberWrapper:
    def __init__(self, post_id=None):
        self.post_id = post_id
        self.utc = None
        self.subcount = None
        self.subreddit = None

    def get_from_submission(self, sub):
        self.get_from_list((str(sub.id),
                            sub.created_utc,
                            sub.subreddit_subscribers,
                            sub.subreddit
                            ))

    # Populate the object from a list of data
    def get_from_list(self, params):
        self.post_id = params[subscribers_field["post_id"]]
        self.utc = params[subscribers_field["utc"]]
        self.subcount = params[subscribers_field["subcount"]]
        self.subreddit = params[subscribers_field["subreddit"]]


class CommentWrapper:
    def __init__(self, comment_id=None):
        self._id = comment_id
        self.body = None
        self.parent_id = None
        self.submission = None
        self.link_id = None
        self.created_utc = None
        self.permalink = None
        self.score = None
        self.ups = None
        self.downs = None
        self.author = None

    def get_from_comment(self, c):
        self.get_from_list((str(c.id),
                            str(c.body),
                            str(c.parent_id),
                            str(c.submission.id),
                            str(c.link_id),
                            c.created_utc,
                            str(c.permalink),
                            c.score,
                            c.ups,
                            c.downs,
                            str(c.author)
                            ))

    # Populate the object from a list of data
    def get_from_list(self, params):
        self._id = params[comment_field["id"]]
        self.body = fix_title(params[comment_field["body"]])
        self.parent_id = params[comment_field["parent_id"]]
        self.submission = params[comment_field["submission"]]
        self.link_id = params[comment_field["link_id"]]
        self.created_utc = params[comment_field["created_utc"]]
        self.permalink = fix_title(params[comment_field["permalink"]])
        self.score = params[comment_field["score"]]
        self.ups = params[comment_field["ups"]]
        self.downs = params[comment_field["downs"]]
        self.author = params[comment_field["author"]]


post_field = {
    "id" : 0,
    "title" : 1,
    "permalink" : 2,
    "shortlink" : 3,
    "url" : 4,
    "author" : 5,
    "timestamp" : 6,
    "created_utc" : 7,
    "type" : 8,
    "subreddit" : 9
}

post_stats_field = {
    "post_id" : 0,
    "score" : 1,
    "ups" : 2,
    "downs" : 3,
    "upvote_ratio" : 4,
    "view_count" : 5,
    "num_comments" : 6,
    "over_18" : 7,
    "archived" : 8,
    "link_flair_text" : 9
}

subscribers_field = {
    "post_id" : 0,
    "utc" : 1,
    "subcount" : 2,
    "subreddit" : 3
}

comment_field = {
    "id" : 0,
    "body" : 1,
    "parent_id" : 2,
    "submission" : 3,
    "link_id" : 4,
    "created_utc" : 5,
    "permalink" : 6,
    "score" : 7,
    "ups" : 8,
    "downs" : 9,
    "author" : 10,
}