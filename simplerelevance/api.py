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

        """
        self.api_url = "https://www.simplerelevance.com/api/v3/"
        self.api_key = api_key
        self.async = async
        self.business_name = business_name

    def authorize(self, request):
        """
        :param request: Request instance to authorize the request.
        :type request: urllib2.Request

        :rtype: urllib2.Request
        """
        base64encoded = base64.encodestring(
            "{0}:{1}".format(self.business_name, self.api_key)
        ).replace('\n', '')
        request.add_header('Authorization', 'Basic {0}'.format(base64encoded))

        return request

    def request_opener(self, request, method=None):
        """
         Provides simple JSON serializing on data, and return simple
        exception where an error occurred.

        :param request: Request instance for sending to the server.
        :type request: urllib2.Request

        :param method: Request method.
        :type method: str

        :rtype: dict
        """
        method = method.upper()
        if method in ['PUT', 'DELETE']:
            request.get_method = lambda: method
        else:
            raise ValueError("'%s' is not supported.")

        try:
            return urllib2.urlopen(self.authorize(request)).read()
        except urllib2.URLError as e:
            raise urllib2.URLError("%s:\n\t%s" % (e.code, e.read()))

    def get(self, endpoint, params):
        """
        :param endpoint: API endpoint to send request to. ex; users/
        :type endpoint: str

        :param params: Data parameters to encode and send through request.
        :type params: dict

        :rtype: dict
        """
        params = urllib.urlencode(params)

        return self.request_opener(
            urllib2.Request("%s%s?%s" % (self.api_url, endpoint, params))
        )

    def post(self, endpoint, data):
        """
        :param endpoint: API endpoint for sending request to. ex; users/
        :type endpoint: str

        :param data: Data/Payload to send over request.
        :type data: dict

        :rtype: dict
        """
        data.update({
            'async': self.async,
        })
        data = urllib.urlencode(data)

        return self.request_opener(
            urllib2.Request("%s%s" % (self.api_url, endpoint), data)
        )

    def users(self, user_email=None, user_external_id=None,
              city=None, state=None, market=None, zipcode=None,
              radius=None, attribute_guids_or=None, attribute_guids_and=None,
              batch_guids=None, return_time_of_day=None):
        """
         The following request params either filter user returns or
        modify what information is returned, as described:

        :param user_email: Match users with the given email.
        :type user_email: str

        :param user_external_id: Match users to an ID to match the
         "external_id" field you used when you first uploaded them.
        :type user_external_id: str

        :param city Match users near the given city/state combo.
         Requires city and state.
        :type city: str

        :param state: Match users near the given city/state combo.
         Requires city and state.
        :type state: str

        :param market: Match users near the given market.
        :type market: str

        :param zipcode: Match users near the given zipcode.
        :type zipcode: str

        :param radius: Match users with any of the given attributes, using
         the global IDs of the attributes (see the attributes/ hook).
        :type radius: str

        :param attribute_guids_or: Match users with all of the given
         attributes, using the global IDs of the attributes.
        :type attribute_guids_or: str

        :param attribute_guids_and: Match users to a list of guids
         (guid is a global ID returned by this hook for each user)
        :type attribute_guids_and: str

        :param batch_guids: Match users to a list of guids (guid is a
         global ID returned by this hook for each user).
        :type batch_guids: str

        :param return_time_of_day: Include the average time of day that each
         user has interacted with your site in the past - this is a boolean
         which defaults to false in the interest of speed.
        :type return_time_of_day: str

        :rtype: dict
        """
        if (city or state) and (not city or not state):
            raise ValueError("'city', 'state' required to both be provided")

        params = {}
        for k, v in locals().items():
            if v is not self and k and v:
                params[k] = v

        return self.get('users/', params)

    def add_user(self, email, zipcode=None, user_id=None, data_dict={}):
        """
         The only required parameter is "email". Optional are zipcode,
        user_id, data_dict. The data_dict can contain and reserved an
        non-reserved attributes you wish to add (see the reserved section of
        these docs for details).

        :param email: The email address of the user.
        :type email: str

        :param zipcode: User ZipCode(Optional).
        :type zipcode: str

        :param user_id: ID of the user(Optional).
        :type user_id: int

        :param data_dict: The data_dict works on key=>value pairs, so do not
        duplicate keys for unrelated attributes(Optional).
        :type data_dict: list of dict

        :rtype: dict
        """
        post_data = {
            'email': email,
            'user_id': user_id,
            'data_dict': json.dumps(data_dict)
        }

        if zipcode:
            post_data['zipcode'] = zipcode

        return self.post('users/', post_data)

