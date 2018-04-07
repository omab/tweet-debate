"""Quick flask app to load and show conversations"""

import re
import json

from flask import Flask, render_template, request, redirect, url_for

from .fetch import Client
from .cache import cache_get, cache_set
from .settings import TWITTER_API_KEY, \
                      TWITTER_API_SECRET, \
                      TWITTER_ACCESS_TOKEN_KEY, \
                      TWITTER_ACCESS_TOKEN_SECRET, \
                      TWEET_ID


app = Flask(__name__)

HANDLE_RE = re.compile('@(\S+)', re.MULTILINE)

CLIENT = Client({
    'consumer_key': TWITTER_API_KEY,
    'consumer_secret': TWITTER_API_SECRET,
    'access_token_key': TWITTER_ACCESS_TOKEN_KEY,
    'access_token_secret': TWITTER_ACCESS_TOKEN_SECRET
})


@app.template_filter('linkify_handles')
def linkify_handles(text):
    for handle in HANDLE_RE.findall(text):
        text = text.replace(
            '@{handle}'.format(handle=handle),
            '<a href="https://twitter.com/{handle}">@{handle}</a>'.format(
                handle=handle
            )
        )
    return text

@app.route('/', methods=['GET', 'POST'])
def index():
    """Index page"""
    if request.method == 'POST':
        tweet_url = request.form['url'].rstrip('/')
        tweet_id = int(tweet_url.split('/')[-1])
        cached_value = cache_get(tweet_id)
        if not cached_value:
            tweet = CLIENT.tweet(tweet_id)
            tweets = CLIENT.conversation(tweet)
            cache_set(tweet_id, [msg for msg in tweets])
        return redirect(url_for('conversation', tweet_id=tweet_id))
    else:
        return render_template('index.html', url=None)


@app.route('/<int:tweet_id>', methods=['GET'])
def conversation(tweet_id):
    """Load cached conversation"""
    return render_template('conversation.html',
                           conversation=cache_get(tweet_id))
