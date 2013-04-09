import urllib2
import json

class SimpleRelevance(object):
    def __init__(self, api_key, business_name, async=0):
        """

        :param api_key: Your password is your API key.
        get it from https://www.simplerelevance.com/dashboard/api-key
        :type api_key: str

        :param business_name: Business name you signed up with,
        all lowercase, replacing spaces with underscores.
        you can see this business name on the front page of your dashboard,
        upper right hand side.
        :type business_name: str

        :param async: When you are done testing, set async=1. This will speed up API
        response times by a factor of 2 or 3.
        :type async: int
        :return:
        """
        self.api_url = "https://www.simplerelevance.com/api/v3/"
        self.api_key = api_key
        self.async = async

        # Create a password manager
        password_mgr = urllib2.HTTPPasswordMgrWithDefaultRealm()
        password_mgr.add_password(None, self.api_url, business_name, api_key)

        handler = urllib2.HTTPBasicAuthHandler(password_mgr)

        # Create "opener" (OpenDirector instance)
        self.opener = urllib2.build_opener(handler)

        # Install the opener.
        # Now all calls to urllib2.urlopen use our opener
        urllib2.install_opener(self.opener)
