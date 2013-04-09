import json
import requests


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
        self.business_name = business_name

    def request_opener(self, endpoint, data=None):
        """
        Really handy shortcut for querying API.

         Provides simple JSON serializing on data, and return simple
        exception where an error occurred.

        :param endpoint: API endpoint to send request to. ex; users/
        :type endpoint: str
        :param data: Data/Payload to send over request.
        :type data: dict
        :return: dict
        # """
        # try:
        #     return json.loads(self.opener.open(
        #         '{0}/{1}'.format(self.api_url, endpoint), data).read())
        # except urllib2.HTTPError as e:
        #     raise urllib2.URLError("{0}:\n\t{1}".format(e.code, e.read()))
        pass

    def _post(self, endpoint, post_data):
        """

        :param endpoint: API endpoint to send request to. ex; users/
        :type endpoint: str
        :param post_data: Data/Payload to send over request.
        :type post_data: dict
        :return: dict
        """
        data = {
            'async': self.async,
            'data': json.dumps(post_data)
        }
        return requests.post(
            "{0}{1}".format(self.api_url, endpoint),
            data=data, auth=(self.business_name, self.api_key)
        )

    def _get(self, endpoint, get_params):
        return requests.get(
            "{0}{1}".format(self.api_url, endpoint), params=get_params,
            auth=(self.business_name, self.api_key)
        )
