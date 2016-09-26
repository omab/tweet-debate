#!/usb/bin/env python

from os import path

from debate.app import app
from debate.cache import load_from_json
from debate.settings import TWEET_ID

if __name__ == '__main__':
    load_from_json(TWEET_ID, path.join(path.dirname(__file__), 'tweets.json'))
    app.run(debug=True)
