import praw
import praw.models
import logging
import mysql.connector
import bottools
import datetime
import botclasses
from pprint import pprint

handler = logging.StreamHandler()
handler.setLevel(logging.DEBUG)
logger = logging.getLogger('prawcore')
logger.setLevel(logging.DEBUG)
logger.addHandler(handler)

print(reddit.user.me())
subreddit = reddit.subreddit('analog')
#print(subreddit.subscribers)

#submissions = reddit.subreddit('analog').hot(limit=1)
submission = reddit.submission(id='a1rp25')
print(submission.title)
pprint(vars(submission))
#for submission in submissions:
#    print(submission.title)
#    pprint(vars(submission))

# print(submission.title)
# print(submission.created)
# print(submission.created_utc)
# pprint.pprint(vars(submission))
# for tlc in submission.comments:
#     pprint.pprint(vars(tlc))
# while True:
#     try:
#         submission.comments.replace_more()
#         break
#     except PossibleExceptions:
#         print('Handling replace_more exception')
#         sleep(1)

# gets a post from the database
# post = reddit_post("9odg8j", db)

# commits a post to the database
# post.commit_to_db(db)

# db.close()

# Creates an empty post, called after reddit query, populated with data, then committed.
#post2 = reddit_post()
