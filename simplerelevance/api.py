import base64
import json
import urllib
import urllib2
from simplerelevance.constants.actiontype import ActionType
from simplerelevance.constants.endpoint import EndPoint
from simplerelevance.utils import pair_required


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
            return json.loads(urllib2.urlopen(self.authorize(request)).read())
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

        return self.get(EndPoint.USERS, params)

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

        return self.post(EndPoint.USERS, post_data)

    def user_delete(self, user_guid, user_external_id=None):
        """
        Delete users one at a time by passing user_guid or user_external_id.

        :param user_guid: Match user to an "user_guid".
        :type user_guid: str

        :param user_external_id: Match user to an "user_external_id".
        :type user_external_id: str

        :rtype: dict
        """
        data = {}
        for k, v in locals().items():
            if v is not self and k and v:
                data[k] = v

        return self.delete(EndPoint.USERS, data)

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

        return self.get(EndPoint.ITEMS, params)

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

        return self.post(EndPoint.ITEMS, post_data)

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

        return self.post(EndPoint.ITEMS, post_data)

    def item_delete(self, item_guid, item_external_id=None):
        """
         Delete items one at a time by passing ``item_guid`` or
        ``item_external_id``.

        :param item_guid:  Match items to a guid.
        :type item_guid: str

        :param item_external_id: Match items to an ID to match the
         "external_id" field you used when you first uploaded them.
        :type item_external_id: str

        :rtype: dict
        """
        data = {}

        for k, v in locals().items():
            if v is not self and k and v:
                data[k] = v

        return self.delete(EndPoint.ITEMS, data)

    def actions(self, user_guid=None, item_guid=None, city=None, state=None,
                latitude=None, longitude=None, action_type=ActionType.CLICKS,
                market=None, zipcode=None, radius=None,
                item_attribute_guids_or=None, item_attribute_guids_and=None,
                user_attribute_guids_or=None, user_attribute_guids_and=None,
                datetime_start=None, datetime_end=None):
        """
         Get Actions, can filter action returns or modify what information
        returned

        :param user_guid: Match actions with the given user, by user guid.
        :type user_guid: str

        :param item_guid: Match actions with the given item, by item guid.
        :type item_guid: str

        :param city: Match actions near the given city/state combo.
         Requires city and state.
        :type city: str

        :param state: Match actions near the given city/state combo.
         Requires city and state.
        :type state: str

        :param latitude: Match actions near the given lat/lon combo.
         Requires latitude and longitude.
        :type latitude: str

        :param longitude: Match actions near the given lat/lon combo.
         Requires latitude and longitude.
        :type longitude: str

        :param action_type: Filter actions by action type.
         0 for clicks,1 for purchases, 5 for email opens.
        :type action_type: ActionType

        :param market: Match actions near the given lat/lon combo.
         Requires latitude and longitude.
        :type market: str

        :param zipcode: Match actions near the given lat/lon combo.
         Requires latitude and longitude.
        :type zipcode: str

        :param radius: Sets the radius, in rough miles, of location searches.
        :type radius: str

        :param item_attribute_guids_or: Match actions concerning items with
         any of the given attributes, using the global IDs of the attributes
         (see the attributes/ hook).
        :type item_attribute_guids_or: list

        :param item_attribute_guids_and: Match actions concerning items with
         all of the given attributes, using the global IDs of the attributes
         (see the attributes/ hook).
        :type item_attribute_guids_and: list

        :param user_attribute_guids_or: Match actions concerning users with
         any of the given attributes, using the global IDs of the attributes
         (see the attributes/ hook).
        :type user_attribute_guids_or: list

        :param user_attribute_guids_and: Match actions concerning users with
         all of the given attributes, using the global IDs of the attributes
         (see the attributes/ hook).
        :type user_attribute_guids_and: list

        :param datetime_start: Return actions within the given datetimes.
         Both or neither are required.
        :type datetime_start: str

        :param datetime_end:  Return actions within the given datetimes.
         Both or neither are required.
        :type datetime_end: str

        :rtype: dict
        """
        pair_required(city, state)
        pair_required(datetime_start, datetime_end)

        params = {}
        for k, v in locals().items():
            if v is not self and k and v:
                params[k] = v

        return self.get(EndPoint.ACTIONS, params)

    def action_add(self, item_id, item_name=None, user_email=None,
                   user_id=None, action_type=ActionType.CLICKS):
        """
         Required parameters include:
        - item_id or item_name (or both),
        - user_id or email (or both),
        - and action_type (see above).

         Highly suggested parameters include timestamp (in UTC), price, zipcode, and,
        if you are matching a preexisting item by name and not by item_id, item_type.

        :param item_id: Match actions with the given item_id.
        :type item_id: int

        :param item_name: Match actions with the given item_name.
        :type item_name: str

        :param user_id: Match actions with the given user_id.
        :type user_id: int

        :param user_email: Match actions with given email.
        :type user_email: str

        :param action_type: Filter actions by action type.
         0 for clicks,1 for purchases, 5 for email opens.
        :type action_type: ActionType

        :rtype: dict
        """
        return self.action_update(item_id, item_name,
                                  user_email, user_id, action_type)

    def action_update(self, item_id, item_name=None, user_email=None,
                      user_id=None, action_type=ActionType.CLICKS):
        """
        Required parameters include:
        - item_id or item_name (or both),
        - user_id or email (or both),
        - and action_type (see above).

        :param item_id: Match actions with the given item_id.
        :type item_id: int

        :param item_name: Match actions with the given item_name.
        :type item_name: str

        :param user_id: Match actions with the given user_id.
        :type user_id: int

        :param user_email: Match actions with given email.
        :type user_email: str

        :param action_type: Filter actions by action type.
         0 for clicks,1 for purchases, 5 for email opens.
        :type action_type: ActionType

        :rtype: dict
        """
        data = {}

        for k, v in locals().items():
            if v is not self and k and v:
                data[k] = v

        # dirty patching api
        items = self.items(item_external_id=data.pop('item_id'))
        data['item_guid'] = items['results'][0]['purchases']['1']['item_guid']

        if user_email:
            users = self.users(user_email=data.pop('user_email'))
            data['user_guid'] = users['results'][0]['guid']

        if user_id:
            users = self.users(user_external_id=self.pop('user_id'))
            data['user_external_id'] = users['results'][0]['external_id']

        return self.post(EndPoint.ACTIONS, data)

    def action_delete(self):
        """
        Raise an error because action termination is not supported.
        """
        raise NotImplementedError(
            """You cannot delete actions via API at this time.
            Please email us if this becomes an issue."""
        )

    def attributes(self, class_id, guid, attribute_name=None, guidlist=None,
                   return_type=None):
        """
        :param class_id: Match attributes for items (1) or users (0).
        :type class_id: int

        :param guid: Update an attribute with this guid.
        :type guid: int

        :param attribute_name: Match attributes by name.
        :type attribute_name: str

        :param guidlist: Retrieve a list of attributes matching guids.
        :type guidlist: list

        :param return_type: A value of "simple" here will result in a smaller,
         faster response.
        :type return_type: str

        :rtype: dict
        """
        params = {}

        for k, v in locals().items():
            if v is not self and k and v:
                params[k] = v

        return self.get(EndPoint.ATTRIBUTES, params)

    def attribute_add(self):
        raise NotImplementedError(
            """All attributes should be initially created as part of a POST to
             /user or /item. See the "Reserved Keys" section for more details.
             Note that you can (unRESTfully) use the PUT hook to create attributes,
             if you must"""
        )

    def attribute_update(self, class_id, guid, user_guid, item_guid,
                         attribute_name, attribute_value):
        """
        :param class_id: Set whether this is a user (0) or item (1) attribute.
        :param class_id: int

        :param guid: Only use this when you want to add an attribute to a
         given user or item. This will be the guid of the attribute you
         want to add.
        :type guid: int

        :param user_guid: The user or item that you wish to add the attribute
         to, in combination with guid above.
        :type user_guid: int

        :param item_guid: The user or item that you wish to add the attribute
         to, in combination with guid above.
        :type item_guid: int

        :param attribute_name: Update an attribute with this name.
        :type attribute_name: str

        :param attribute_value: Update an attribute with this value
         (keep in mind that attributes are name -> value pairs, where you can
         have multiple values for each name).
        :type attribute_value str

        :rtype: dict
        """
        data = {}

        for k, v in locals().items():
            if v is not self and k and v:
                data[k] = v

        return self.put(EndPoint.ATTRIBUTES, data)

    def attribute_delete(self, guid, user_guid=None, item_guid=None,
                         attribute_name=None):
        """
        :param guid: The guid of the attribute to delete.
        :type guid: int

        :param user_guid: If you use this with guid above, this hook
         will remove the attribute from the given user or item, rather than
        :type user_guid: int

        :param item_guid: If you use this with guid above, this hook
         will remove the attribute from the given user or item, rather than
         deleting it entirely.
        :type item_guid: int

        :param attribute_name: Delete all attributes with the given name.
        :type attribute_name: str

        :rtype: dict
        """
        data = {}

        for k, v in locals().items():
            if v is not self and k and v:
                data[k] = v

        return self.delete(EndPoint.ATTRIBUTES, data)

    def predictions(self, email):
        """
        :param email: The email to fetch for.
        :type email: str

        :rtype: dict
        """
        return self.get(EndPoint.PREDICTIONS, {'email': email})

