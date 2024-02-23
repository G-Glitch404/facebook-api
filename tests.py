from main import FacebookAPI

facebook_api = FacebookAPI('Username', 'Password')
facebook_api.login()


def test_friend_requests():
    return facebook_api.friend_requests('FB_ID')
