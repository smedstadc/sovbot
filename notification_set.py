import requests
import yaml
from lxml import etree
from collections import OrderedDict
from pony.orm import db_session
from models import Notification
from twisted.python import log
from notification_formatter import NotificationFormatter

class NotificationSet(object):
    """Object for processsing notifications from the Eve: Online XML API."""
    def __init__(self, selected_types, key_id, vcode, character_id=None):
        """
        Creates a new NotificationSet and associates it with an API Key. It is only necessary to specify a character_id
        if the given API key has multiple characters. Selected types should be a dictionary with notification typeIDs as
        keys, and short descriptions as values. When notifications are pulled they will be filtered out of the set after
        their headers are recorded if they're not in the set of selected typeIDs.

        Visit https://neweden-dev.com/Char/Notifications#Notification_Types for a full list of notification typeIDs.
        """
        self.key_id = key_id
        self.vcode = vcode
        self.character_id = character_id
        self.selected_types = selected_types
        self._headers_tree = None
        self._texts_tree = None
        self._notifications = OrderedDict()
        self._names = None

    def get_headers_xml(self):
        """Grabs notification headers from the API and stores them in the object."""
        uri = 'https://api.eveonline.com/char/Notifications.xml.aspx'
        params = self._params()
        response = requests.get(uri, params=params)
        log.msg("Incoming Notification Headers XML:\n{content}".format(content=response.content))
        self._headers_tree = etree.fromstring(response.content)

    def get_texts_xml(self):
        """Grabs notification contents from the API and stores them in the object."""
        notification_ids = [row.attrib['notificationID'] for row in self._headers_tree.xpath('result/rowset/row') if row.attrib['typeID'] in self.selected_types.keys()]
        uri = 'https://api.eveonline.com/char/NotificationTexts.xml.aspx'
        params = self._params()
        params['IDs'] = ','.join(notification_ids)
        response = requests.get(uri, params=params)
        log.msg("Incoming Notification Texts XML:\n{content}".format(content=response.content))
        self._texts_tree = etree.fromstring(response.content)

    def build_notifications(self):
        """Combines data from headers and into a single notificationID indexed hash that can be iterated over."""
        for row in self._headers_tree.xpath('result/rowset/row'):
            attributes = dict(row.attrib)
            if attributes['typeID'] in self.selected_types:
                self._notifications[attributes['notificationID']] = attributes

        for row in self._texts_tree.xpath('result/rowset/row'):
            attributes = dict(row.attrib)
            self._notifications[attributes['notificationID']]['body'] = yaml.load(row.text)

    def fetch_character_names(self):
        """Fetches names by id from the Eve API and stores them in a dictionary for later use in messages."""
        name_id_types = ['aggressorAllianceID', 'aggressorCorpID', 'aggressorID', 'corpID', 'allianceID']
        name_ids = set()
        for key in self._notifications.keys():
            if 'body' in self._notifications[key]:
                for id_key in name_id_types:
                    if id_key in self._notifications[key]['body']:
                        name_ids.add(self._notifications[key]['body'][id_key])
            else:
                log.msg("Tried to get names for a notification without a body: {}".format(self._notifications[key]))

        uri = 'https://api.eveonline.com/eve/CharacterName.xml.aspx'
        # The `if name_id` clause in the list comprehension below ensures None values can't sneak in and
        # cause the Eve API to return an error that would prevent us from populating the id->name mapping.
        params = {'IDs': ','.join([str(name_id) for name_id in name_ids if name_id])}
        response = requests.get(uri, params=params)
        log.msg("Incoming Names XML:\n{content}".format(content=response.content))
        names_tree = etree.fromstring(response.content)
        self._names = {row.attrib['characterID']: row.attrib['name'] for row in names_tree.xpath('result/rowset/row')}

    def get_messages(self):
        """Yields notification message object for each notification which is new."""
        notification_decorator = NotificationFormatter(self._names)
        messages = []
        for notification in self._notifications.itervalues():
            if self._notification_is_new(notification):
                log.msg("Creating message for type {type} with body {body}.".format(type=notification['typeID'], body=notification['body']))
                messages.append(notification_decorator.format(notification))
                with db_session:
                    log.msg("Saving notification so it won't be repeated.")
                    n = Notification(id=notification['notificationID'], type_id=notification['typeID'], sent_date=notification['sentDate'])
            else:
                log.msg("Skipping repeat message for {}.".format(notification['notificationID']))
        return messages

    def _params(self):
        """Helper method used to provide required parameters for API request URIs."""
        params = {'keyID': self.key_id, 'vcode': self.vcode}
        if self.character_id:
            params['characterID'] = self.character_id
        return params

    @staticmethod
    @db_session
    def _notification_is_new(notification):
        """Returns true if a notificationID hasn't been seen before."""
        notification_id = notification['notificationID']
        n = Notification.get(id=notification_id)
        return bool(n is None)
