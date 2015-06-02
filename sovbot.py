"""SovBot: An Eve bot that spams notifications from the Eve API"""

import logging
import settings
from notification_set import NotificationSet
from twisted.python import log
from twisted.internet import reactor
from twisted.internet.defer import Deferred
from twisted.internet import task
from twisted.words.protocols.jabber.jid import JID
from wokkel.client import XMPPClient
from wokkel.muc import MUCClient



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
    """Joins a room and announces selected notifications every 30 minutes."""

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
        log.msg("Starting notifications task...")
        notification_set = NotificationSet(SELECTED_TYPES, KEY_ID, VCODE)
        d = Deferred()
        d.addCallback(self._get_headers)
        d.addCallback(self._get_texts)
        d.addCallback(self._build_notifications)
        d.addCallback(self._fetch_names)
        d.addCallback(self._send_messages)
        d.addCallback(self._log_success)
        d.addErrback(self._log_exceptions)
        d.callback(notification_set)

    def _get_headers(self, notification_set):
        log.msg("Fetching headers from API...")
        notification_set.get_headers_xml()
        return notification_set

    def _get_texts(self, notification_set):
        log.msg("Fetching texts from API...")
        notification_set.get_texts_xml()
        return notification_set

    def _build_notifications(self, notification_set):
        log.msg("Building notifications...")
        notification_set.build_notifications()
        return notification_set

    def _fetch_names(selfself, notification_set):
        log.msg("Fetching character names...")
        notification_set.fetch_character_names()
        return notification_set

    def _send_messages(self, notification_set):
        log.msg("Sending notification messages...")
        for message in reversed(notification_set.get_messages()):
            body = message
            self.groupChat(self.room_jid, body)
        return notification_set

    def _log_success(self, notification_set):
        log.msg("Task finished successfully.")
        return True

    def _log_exceptions(self, failure):
        log.msg("Exception:{}".format(failure.getErrorMessage()))
        log.msg("Traceback:{}".format(failure.getTraceback()))
        body = "Is it just me, or is the internet on fire?"
        self.groupChat(self.room_jid, body)


if __name__ == "__main__":
    # set up logging.
    FORMAT = '%(asctime)s :: %(message)s'
    logging.basicConfig(filename='sovbot.log', format=FORMAT, level=logging.INFO)
    observer = log.PythonLoggingObserver(loggerName='sovbot')
    observer.start()

    # set up client.
    client = XMPPClient(THIS_JID, PASSWORD)
    client.logTraffic = LOG_TRAFFIC
    mucHandler = SovBot(ROOM_JID, NICKNAME)
    mucHandler.setHandlerParent(client)
    client.startService()
    reactor.run()
