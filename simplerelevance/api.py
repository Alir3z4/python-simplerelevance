import base64
import json
import urllib
import urllib2

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

        :param async: When you are done testing, set async=1.
        This will speed up API
        response times by a factor of 2 or 3.
        :type async: int

        :return:
        """
        self.api_url = "https://www.simplerelevance.com/api/v3/"
        self.api_key = api_key
        self.async = async
        self.business_name = business_name

    def authorize(self, request):
        """
        :param request: Request instance to authorize the request.
        :type request: urllib2.Request
        :return: urllib2.Request
        """
        base64encoded = base64.encodestring(
            "{0}:{1}".format(self.business_name, self.api_key)
        ).replace('\n', '')
        request.add_header('Authorization', 'Basic {0}'.format(base64encoded))

        return request

    def request_opener(self, request):
        """
         Provides simple JSON serializing on data, and return simple
        exception where an error occurred.

        :param request: Request instance for sending to the server.
        :type request: urllib2.Request
        :return: urllib2.Request
        """
        try:
            return json.loads(urllib2.urlopen(self.authorize(request)).read())
        except urllib2.URLError as e:
            raise urllib2.URLError("{0}:\n\t{1}".format(e.code, e.read()))

    def get(self, endpoint, params):
        """
        :param endpoint: API endpoint to send request to. ex; users/
        :type endpoint: str
        :param params: Data parameters to encode and send through request.
        :type params: dict
        :return: dict
        """
        params = urllib.urlencode(params)

        return self.request_opener(
            urllib2.Request("{0}{1}".format(self.api_url, endpoint), params)
        )

    def post(self, endpoint, data):
        """
        :param endpoint: API endpoint to send request to. ex; users/
        :type endpoint: str
        :param data: Data/Payload to send over request.
        :type data: dict
        :return: dict
        """
        data = {
            'async': self.async,
            'data': data
        }

        return self.request_opener(
            urllib2.Request("{0}{1}".format(self.api_url, endpoint), data)
        )
