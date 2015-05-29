# copy this into a 'settings.py' file to configure the bot
keyid = 'my eve api keyid'
vcode = 'my eve api vcode'
jid = 'my jid'
password = 'my password'
room = 'my room jid'
nickname = 'my nickname'
log_traffic = False
task_interval = 1800.0  # 30 minutes

# Reference: https://neweden-dev.com/Char/Notifications#Notification_Types
# Keys must match notification typeIDs, values can be any short description you like, keeping in mind that they'll be
# used to generate messages.
selected_types = {'38': 'Sovereignty claim fails',  # (Corporation version)
                  '40': 'Sovereignty bill late',  # (Corporation version)
                  '42': 'Sovereignty claim lost',  # (Corporation version)
                  '44': 'Sovereignty claim acquired',  # (Corporation version)
                  '45': 'Alliance anchoring alert',
                  '46': 'Alliance structure turns vulnerable',
                  '47': 'Alliance structure turns invulnerable',
                  '48': 'Sovereignty disruptor anchored',
                  '49': 'Structure won/lost',
                  '75': 'Tower alert',
                  '76': 'Tower resource alert',
                  '77': 'Station service aggression message',
                  '78': 'Station state change message',
                  '79': 'Station conquered message',
                  '80': 'Station aggression message',
                  '86': 'Territorial Claim Unit under attack',
                  '87': 'Sovereignty Blockade Unit under attack',
                  '88': 'Infrastructure Hub under attack',
                  '93': 'Customs office has been attacked',
                  '94': 'Customs office has entered reinforced',
                  '95': 'Customs office has been transferred'}
