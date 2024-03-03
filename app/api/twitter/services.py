from dotenv import load_dotenv
import tweepy
import os


load_dotenv()


class TwitterAPIService:
    def __init__(self) -> None:
        self.TWITTER_BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

    def get_tweets(self, query: str):
        try:
            twitter_client = tweepy.Client(
                bearer_token=self.TWITTER_BEARER_TOKEN)
            response = twitter_client.search_recent_tweets(
                query,
                media_fields=['preview_image_url'],
                expansions=['attachments.media_keys'],
                max_results=10)

            if response is None:
                return None, None

            media = {}
            if response.includes.get('media'):
                media = {m["media_key"]: m for m in response.includes['media']}

            images_urls_set = set()
            tweets_text_set = set()

            for tweet in response.data:
                tweet_str = str(tweet.text)
                tweets_text_set.add(tweet_str)
                attachments = tweet.attachments
                if isinstance(attachments, dict) and 'media_keys' in attachments and media:
                    media_keys = attachments.get('media_keys')
                    for key in media_keys:
                        if key in media and media[key].preview_image_url:
                            images_urls_set.add(media[key].preview_image_url)

            images_urls_list = list(images_urls_set)[:4]
            images_urls = {f"img_url{i+1}": value for i,
                           value in enumerate(images_urls_list)}
            tweets = '; '.join(tweets_text_set)
            return tweets, images_urls

        except Exception as e:
            print(f"An unexpected error occurred: {e}")
            return None, None


if __name__ == "__main__":
    api = TwitterAPIService()
    tweets, images = api.get_tweets("@RBC")
    print(f"TWEETS: {tweets}\nIMAGEs: {images}")
