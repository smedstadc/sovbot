"""SovBot: An Eve bot that spams notifications from the Eve API"""

import logging
from twisted.internet import task
from twisted.python import log
from twisted.words.protocols.jabber.jid import JID
from wokkel.client import XMPPClient
from wokkel.muc import MUCClient
from twisted.internet import reactor
import settings


# Configuration parameters

THIS_JID = JID(settings.jid)
ROOM_JID = JID(settings.room)
NICKNAME = settings.nickname
PASSWORD = settings.password
LOG_TRAFFIC = settings.log_traffic
TASK_INTERVAL = settings.task_interval


class SovBot(MUCClient):
    """Joins a room and announces sov notifications every 30 minutes."""

    def __init__(self, room_jid, nick):
        MUCClient.__init__(self)
        self.room_jid = room_jid
        self.nick = nick
        self.looping_task = task.LoopingCall(self.do_task)

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
        log.msg("Joining room...")
        log.msg("Start looping task...")
        self.looping_task.start(TASK_INTERVAL)

    def receivedGroupChat(self, room, user, message):
        """Handle received groupchat messages."""
        log.msg("Received groupchat...".format(message.body))

    def do_task(self):
        log.msg("Test Task Ping...")


if __name__ == "__main__":
    # set up logging.
    logging.basicConfig(filename='sovbot.log', level=logging.DEBUG)
    logger = logging.getLogger('sovbot')
    observer = log.PythonLoggingObserver(loggerName='sovbot')
    observer.start()

    # set up client.
    client = XMPPClient(THIS_JID, PASSWORD)
    client.logTraffic = LOG_TRAFFIC
    mucHandler = SovBot(ROOM_JID, NICKNAME)
    mucHandler.setHandlerParent(client)
    client.startService()
    reactor.run()
