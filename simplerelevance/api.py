import base64
import json
import urllib
import urllib2
from simplerelevance.utils import pair_required, expected_be


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

        if method:
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
        data['async'] = self.async
        data = urllib.urlencode(data)

        return self.request_opener(
            urllib2.Request("%s%s" % (self.api_url, endpoint), data)
        )

    def delete(self, endpoint, data):
        """
        Sending DELETE request.

        :param endpoint: API endpoint for sending request to. ex; users/
        :type endpoint: str

        :param data: Data/Payload to send over request.
        :type data: dict

        :rtype: dict
        """
        data = urllib.urlencode(data)

        return self.request_opener(
            request=urllib2.Request("%s%s" % (self.api_url, endpoint), data),
            method='DELETE'
        )

    def put(self, endpoint, data):
        """
        Sending PUT request.

        :param endpoint: API endpoint for sending request to. ex; users/
        :type endpoint: str

        :param data: Data/Payload to send over request.
        :type data: dict

        :rtype: dict
        """
        data = urllib.urlencode(data)

        return self.request_opener(
            request=urllib2.Request("%s%s" % (self.api_url, endpoint), data),
            method='PUT'
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
        pair_required(city, state)

        params = {}
        for k, v in locals().items():
            if v is not self and k and v:
                params[k] = v

        return self.get('users/', params)

    def user_add(self, email, zipcode=None, user_id=None, data_dict={}):
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

    def user_delete(self, user_guid, user_external_id=None):
        """
        Delete users one at a time by passing user_guid or user_external_id.

        :param user_guid: Match user to an "user_guid".
        :type user_guid: int

        :param user_external_id: Match user to an "user_external_id".
        :type user_external_id: int

        :rtype: dict
        """
        data = {}
        for k, v in locals().items():
            if v is not self and k and v:
                expected_be(v, int)
                data[k] = v

        return self.delete('users/', data)

    def items(self, item_name=None, item_external_id=None, item_guid=None,
              city=None, state=None, latitude=None, longtitude=None,
              market=None, zipcode=None, radius=None, attribute_guids_or=None,
              attribute_guids_and=None, variant_filters=None, batch_guids=None,
              skip_useraction_return=False, filter_expired=True):
        """
         Get items, can filter item returns or modify what information
        returned.

        :param item_name: Match items with the given name.
        :type item_name: str

        :param item_external_id: Match items to an ID to match the
         "external_id" field you used when you first uploaded them.
        :type item_external_id: int

        :param item_guid: Match items to a guid. Guids are returned by this
         hook for each item.
        :type item_guid: str

        :param city: Match items to an ID to match the "external_id" field
         you used when you first uploaded them.
        :type city: str

        :param state: Match items to an ID to match the "external_id" field
         you used when you first uploaded them.
        :type state: str

        :param latitude: Match items near the given lat/lon combo.
         Requires latitude and longitude.
        :type latitude: str

        :param longtitude: Match items near the given lat/lon combo.
         Requires latitude and longitude.
        :type longtitude: str

        :param market: Match items near the given market.
        :type market: str

        :param zipcode: Match items near the given zipcode.
        :type zipcode: str

        :param radius: Sets the radius, in rough miles, of location searches.
        :type radius: str

        :param attribute_guids_or: Match items with any of the given
         attributes, using the global IDs of the attributes
         (see the attributes/ hook).
        :type attribute_guids_or: list

        :param attribute_guids_or: Match items with any of the given
         attributes, using the global IDs of the attributes
         (see the attributes/ hook).
        :type attribute_guids_and: list

        :param variant_filters: Match items using properties of their variants.
         Please contact us for help if you'd like to use this hook.
        :type variant_filters: str

        :param batch_guids: Match items to a list of guids.
        :type batch_guids: list

        :param skip_useraction_return: Speeds up this hook by not returning
         any information about purchases of the returned items.
         Defaults to false.
        :type skip_useraction_return: bool

        :param filter_expired: Boolean, defaults to true - only returns items
         that are set to be available in our system.
        :type filter_expired: bool

        :rtype: dict
        """
        pair_required(city, state)
        pair_required(latitude, longtitude)

        params = {}
        for k, v in locals().items():
            if v is not self and k and v:
                params[k] = v

        return self.get('items/', params)

    def item_update(self, item_name, item_id, item_type=None,
                    data_dict={}, variants=[]):
        """
        Update an item match with `item_id`.

        :param item_name: The item's name - this should be unique across your
         database if possible.
        :type item_name: str

        :param item_id: A unique ID for the item from your database.
        :type item_id: str

        :param item_type: This helps the SimpleRelevance system find semantic
         data for your item. You can use any string you want (Optional).
        :type item_type: str

        :param data_dict: A bracketed json encodable dictionary. This can
         have any attributes at all that apply to your item; the more the
         better. See below for the list of reserved attribute names - these
         help SimpleRelevance create semantic connections about your items.
         Note that these include 'starts' and 'expires', in case your items
         are time sensitive.
        :type data_dict: dict

        :param variants: A json encodable list of dictionaries with the same
         format as the data dict. Variants support a subset of the data_dict
         reserved keys. They are used for subtle differences in items - for
         example, multiple sizes of shoe. In general, attributes you apply to
         a variant of an item should not be able to help make a better
         prediction about the person buying the item. Note that you can upload
         an external_id for variants, but it should be unique across all
         items. Otherwise you can upload "sku" or "name", which do not have
         this restriction. You node at least one of these three to save a
         variant at all.
        :type variants: list of dict

        :rtype: dict
        """
        if item_id in ['', 0, None] or not item_id:
            raise ValueError('`item_id` have Unknown value')

        post_data = {
            'item_name': item_name,
            'item_id': item_id,
            'data_dict': json.dumps(data_dict),
            'variants': json.dumps(variants)
        }
        if item_type:
            post_data['item_type'] = item_type

        return self.post('items/', post_data)

    def item_add(self, item_name, item_type=None, data_dict={},
                 variants=[]):
        """
        Add new item.

        :param item_name: The item's name - this should be unique across your
         database if possible.
        :type item_name: str

        :param item_type: This helps the SimpleRelevance system find semantic
         data for your item. You can use any string you want (Optional).
        :type item_type: str

        :param data_dict: A bracketed json encodable dictionary. This can
         have any attributes at all that apply to your item; the more the
         better. See below for the list of reserved attribute names - these
         help SimpleRelevance create semantic connections about your items.
         Note that these include 'starts' and 'expires', in case your items
         are time sensitive.
        :type data_dict: dict

        :param variants: A json encodable list of dictionaries with the same
         format as the data dict. Variants support a subset of the data_dict
         reserved keys. They are used for subtle differences in items - for
         example, multiple sizes of shoe. In general, attributes you apply to
         a variant of an item should not be able to help make a better
         prediction about the person buying the item. Note that you can upload
         an external_id for variants, but it should be unique across all
         items. Otherwise you can upload "sku" or "name", which do not have
         this restriction. You node at least one of these three to save a
         variant at all.
        :type variants: list of dict

        :rtype: dict
        """

        post_data = {
            'item_name': item_name,
            'data_dict': json.dumps(data_dict),
            'variants': json.dumps(variants)
        }
        if item_type:
            post_data['item_type'] = item_type

        return self.post('items/', post_data)
