"""Tweet-Debate Twitter client"""

import twitter


class Client(object):
    """Twitter Client Wrapper"""

    def __init__(self, credentials):
        """
        Instance initialization method

        @param credentials: dict with consumer_key, consumer_secret,
                            access_token_key, access_token_secret
        """
        self._client = None
        self.credentials = credentials

    def conversation(self, tweet):
        """
        Given a tweet, fetch the conversation sparked with other users.
        """
        since_id = tweet.id
        replies = [tweet]
        replies_ids = [tweet.id]
        screen_name = tweet.user.screen_name
        timeline = self.timeline(screen_name, tweet, count=200)

        # collection obvious messages from the user timeline
        for msg in timeline:
            if msg.in_reply_to_status_id in replies_ids:
                replies.append(msg)
                replies_ids.append(msg.id)

        # collect replies to replies to the obvoious message
        for msg in timeline:
            if msg.id not in replies_ids and msg.in_reply_to_status_id:
                replied_to = self.tweet(msg.in_reply_to_status_id)
                if replied_to and replied_to.in_reply_to_status_id in replies_ids:
                    replies += [replied_to, msg]
                    replies_ids += [replied_to.id, msg.id]

        # search replies to messages matched
        while True:
            processed_messages = False
            for msg in self.search(screen_name, since_id):
                if msg.in_reply_to_status_id in replies_ids:
                    replies.append(msg)
                    replies_ids.append(msg.id)
                    since_id = msg.id
                    processed_messages = True

            if not processed_messages:
                break

        return self.sort_messages(self.unique_messages(replies))

    def tweet(self, tweet_id):
        """
        Fetch a single tweet for a given id.
        """
        try:
            return self.client.GetStatus(tweet_id)
        except twitter.TwitterError:
            return None

    def timeline(self, screen_name, tweet, count=100):
        """
        Fetch user timeline since a given tweet.
        """
        messages = [tweet]

        for page in range(0, int(count / 100)):
            messages += self.client.GetUserTimeline(
                screen_name=screen_name,
                since_id=messages[-1].id,
                count=(page + 1) * 100
            )
        return self.sort_messages(messages)

    def search(self, screen_name, since_id):
        """
        Search user replies since a given tweet id.
        """
        messages = self.client.GetSearch(
            'to:{screen_name}'.format(screen_name=screen_name),
            since_id=since_id,
            count=100
        )
        return self.sort_messages(self.unique_messages(messages))

    def sort_messages(self, messages):
        """
        Sort messages by id (the needed chronological order)
        """
        return sorted(messages, key=lambda msg: msg.id)

    def unique_messages(self, messages):
        """
        Return unique messages from a messages set
        """
        messages = {msg.id: msg for msg in messages}
        return list(messages.values())

    @property
    def client(self):
        """
        Twitter API client
        """
        if not self._client:
            self._client = twitter.Api(sleep_on_rate_limit=True, **self.credentials)
            self._client.SetCacheTimeout(60 * 60 * 24)
        return self._client
