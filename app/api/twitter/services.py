from dotenv import load_dotenv
import tweepy
import os


load_dotenv()


class TwitterAPIService:
    def __init__(self) -> None:
        self.BEARER_TOKEN = os.getenv("TWITTER_BEARER_TOKEN")

    def get_tweets(self, query: str):
        try:
            twitter_client = tweepy.Client(self.BEARER_TOKEN)
            response = twitter_client.search_recent_tweets(
                query,
                media_fields=['preview_image_url'],
                expansions=['attachments.media_keys'],
                max_results=100)

            media = {m["media_key"]: m for m in response.includes['media']}

            images_urls_set = set()
            tweets_text_set = set()

            for tweet in response.data:
                tweets_text_set.add(tweet.text)
                attachments = tweet.attachments
                if isinstance(attachments, dict) and 'media_keys' in attachments and media:
                    media_keys = attachments.get('media_keys')
                    for key in media_keys:
                        if key in media and media[key].preview_image_url:
                            images_urls_set.add(media[key].preview_image_url)

            images_urls = list(images_urls_set)[:4]

            # TODO: IMPLEMENT RETURN AND PLATFORM ARGUMENT
            print(images_urls)
            print('; '.join(tweets_text_set))

        except Exception as e:
            print(f"An unexpected error occurred: {e}")


if __name__ == "__main__":
    api = TwitterAPIService()
    twits = api.get_tweets("@elonmusk")
