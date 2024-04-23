import os

import tweepy
from dotenv import load_dotenv

load_dotenv()


class TwitterAPIService:
    def __init__(self) -> None:
        self.TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

    def get_tweets(self, query: str):
        try:
            twitter_client = tweepy.Client(bearer_token=self.TWITTER_BEARER_TOKEN)
            response = twitter_client.search_recent_tweets(
                query,
                media_fields=["url", "media_key"],
                expansions=[
                    "attachments.media_keys",
                    "attachments.media_source_tweet",
                ],
                max_results=10,
                tweet_fields=["attachments", "entities"],
            )

            if response is None:
                return None, None

            images_urls_list = []
            for tweet in response.data:
                # Extract from main Tweet attachments
                if tweet.entities.get("urls"):
                    for url in tweet.entities.get("urls"):
                        if url.get("images"):
                            images_urls_list.extend(
                                [
                                    m["url"]
                                    for m in url.get("images")
                                    if "format=jpg&name=orig" in m["url"]
                                ]
                            )
                if tweet.attachments and tweet.attachments.get("media_keys"):
                    images_urls_list.extend(
                        [
                            m["url"]
                            for m in response.includes["media"]
                            if m.get("type") == "photo"
                            and m["media_key"] in tweet.attachments["media_keys"]
                        ]
                    )

            tweets_list = [tw.text for tw in response.data]

            images_urls = {
                f"img_url{i+1}": value for i, value in enumerate(images_urls_list[:4])
            }
            tweets = "; ".join(tweets_list)
            return tweets, images_urls

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None, None


if __name__ == "__main__":
    api = TwitterAPIService()
    tweets, images = api.get_tweets("@rbc")
    print(f"TWEETS: {tweets}\nIMAGEs: {images}")
