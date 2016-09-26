import json

from twitter import Status


_cache = {}


def cache_get(tweet_id):
    """Retrieve stored messages from a given tweet id"""
    return [Status.NewFromJsonDict(json.loads(tweet))
            for tweet in _cache.get(int(tweet_id), [])]


def cache_set(tweet_id, tweets):
    """Store messages for a given tweet id"""
    _cache[int(tweet_id)] = [tweet.AsJsonString() for tweet in tweets]


def load_from_json(tweet_id, path):
    """Load messages from a json file"""
    with open(path, "r") as tweets_file:
        cache_set(tweet_id, [Status.NewFromJsonDict(tweet)
                             for tweet in json.load(tweets_file)])
