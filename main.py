from requests import Session
from parsel import Selector
import exceptions


class FacebookAPI(Session):
    def __init__(self, user, passwd):
        super(FacebookAPI, self).__init__()
        self.password = passwd
        self.username = user
        self.headers.update({'User-Agent': "Mozilla/5.0 (Windows NT 10; Win64; x64) AppleWebKit (KHTML, like Gecko)"})

    def login(self) -> bool:
        # getting required tokens
        response = self.get("https://mbasic.facebook.com/login.php").text
        select = Selector(text=response, type="html")
        try:
            tokens = [tokens.get() for tokens in select.css('form > input[type="hidden"] ::attr(value)')[:7]]
            data = {'email': self.username, 'pass': self.password, 'lsd': tokens[0],
                    'jazoest': tokens[1], 'm_ts': tokens[2], 'li': tokens[3],
                    'try_number': tokens[4], 'unrecognized_tries': tokens[5],
                    'bi_xrwh': tokens[6], 'login': "Log In"}
        except IndexError: raise exceptions.LoginFailed('Login Failed - selector needs an update')
        else: self.post("https://mbasic.facebook.com/login/device-based/regular/login/?refsrc=deprecated&lwv=100&ref=dbl", data=data)  # logging in

        # checking if logged in
        response = self.get('https://mbasic.facebook.com/home.php').text
        logout_btn = Selector(text=response, type='html').css('#mbasic_logout_button ::text').get() or ''
        if 'logout' in logout_btn.lower():
            return True
        raise exceptions.LoginFailed("Login Failed - Check Your Username and Password")

    def friend_requests(self, fb_id: str) -> bool:
        """ sending a friend request to a user using fb_id e.g. yousifweal264, 100018011926928
                e.g.
                    https://mbasic.facebook.com/yousifweal264
                    https://mbasic.facebook.com/100018011926928 """

        response = self.get(f'https://mbasic.facebook.com/{fb_id}?v=timeline').text

        select = Selector(text=response, type='html')
        add_url = select.css('#m-timeline-cover-section > div > table > tr > td:nth-child(1) > a')
        if add_url is None:
            add_url = select.css('#m-timeline-cover-section > div > table > tbody > tr > td:nth-child(1) > a')

        try:
            if 'add' in add_url.css('::text').extract_first().lower():
                self.get("https://mbasic.facebook.com" + add_url.css('::attr(href)').get())
                return True
        except AttributeError: pass

        raise exceptions.FriendRequestFailed('Friend Request Failed - Check the account ID')
