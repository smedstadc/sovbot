"""SovBot: An Eve bot that spams notifications from the Eve API"""

import logging
import settings
import requests
import notifications
from lxml import etree
from twisted.internet.defer import Deferred, failure
from twisted.internet import task
from twisted.python import log
from twisted.words.protocols.jabber.jid import JID
from wokkel.client import XMPPClient
from wokkel.muc import MUCClient
from twisted.internet import reactor



THIS_JID = JID(settings.jid)
ROOM_JID = JID(settings.room)
NICKNAME = settings.nickname
PASSWORD = settings.password
LOG_TRAFFIC = settings.log_traffic
TASK_INTERVAL = settings.task_interval
KEY_ID = settings.keyid
VCODE = settings.vcode
SELECTED_TYPES = settings.selected_types


class SovBot(MUCClient):
    """Joins a room and announces sov notifications every 30 minutes."""

    def __init__(self, room_jid, nick):
        MUCClient.__init__(self)
        self.room_jid = room_jid
        self.nick = nick
        self.looping_task = task.LoopingCall(self.notifications_task)

    def connectionInitialized(self):
        """Once authorized, join the room."""
        log.msg("Connected...")

        def joinedRoom(room):
            if room.locked:
                log.msg("Room was locked, using default configuration...")
                # The room will be locked if it didn't exist before we joined it.
                # Just accept the default configuration. The room will be public and temporary.
                return self.configure(room.roomJID, {})

        MUCClient.connectionInitialized(self)
        self.join(self.room_jid, self.nick)
        log.msg("Joining {}...".format(self.room_jid))
        log.msg("Start looping task with {} second interval...".format(TASK_INTERVAL))
        self.looping_task.start(TASK_INTERVAL)

    def receivedGroupChat(self, room, user, message):
        """Handle received groupchat messages."""
        # handle force-check here
        pass

    def notifications_task(self):
        """This function defines the task which reports notifications from the Eve API every TASK_INTERVAL seconds."""
        d = Deferred()
        d.addCallback(self._get_notification_headers)
        d.addCallbacks(self._extract_header_attributes, self._handle_request_failure)
        d.addCallbacks(self._get_notification_texts, self._handle_extract_attributes_failure)
        d.callback("http://api.example.com/endpoint.xml")

    def _get_notification_headers(self, path):
        log.msg("In _get_notification_headers...")
        uri = 'http://api.eveonline.com/char/Notifications.xml.aspx'
        response = requests.get(uri, params={'keyID': KEY_ID, 'vcode': VCODE})
        result = response.content
        print result
        return result

    def _handle_request_failure(self, failure):
        log.msg("In _handle_request_failure...")
        log.msg("Exception:{}".format(failure.getErrorMessage()))
        body = "Is it just me, or is the internet on fire?"
        self.groupChat(self.room_jid, body)

    def _extract_header_attributes(self, result):
        log.msg("In _extract_header_attributes...")
        tree = etree.fromstring(result)
        result = [row.attrib for row in tree.xpath('result/rowset/row') if row.attrib['typeID'] in SELECTED_TYPES.keys()]
        for row in result:
            print row
        return result

    def _handle_extract_attributes_failure(self, failure):
        log.msg("In _handle_extract_attributes_failure...")
        log.msg("Exception:{}".format(failure.getErrorMessage()))

    def _get_notification_texts(self, result):
        log.msg("In _get_notification_texts...")
        notification_ids = [row['notificationID'] for row in result]
        notification_types = {row['notificationID']: row['typeID'] for row in result}
        log.msg("Fetching texts for IDs {}".format(','.join(notification_ids)))
        uri = 'http://api.eveonline.com/char/NotificationTexts.xml.aspx'
        response = requests.get(uri, params={'keyID': KEY_ID, 'vcode': VCODE, 'IDs': ','.join(notification_ids)})
        print response.content

if __name__ == "__main__":
    # set up logging.
    logging.basicConfig(filename='sovbot.log', level=logging.INFO)
    observer = log.PythonLoggingObserver(loggerName='sovbot')
    observer.start()

    # set up client.
    client = XMPPClient(THIS_JID, PASSWORD)
    client.logTraffic = LOG_TRAFFIC
    mucHandler = SovBot(ROOM_JID, NICKNAME)
    mucHandler.setHandlerParent(client)
    client.startService()
    reactor.run()
