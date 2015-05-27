"""This is a scratch file for playing with sample xml. It can be deleted later."""

from lxml import etree
import yaml

selected_types = {'38': 'Sovereignty claim fails (corporation)',
                  '40': 'Sovereignty bill late (corporation)',
                  '42': 'Sovereignty claim lost (corporation)',
                  '44': 'Sovereignty claim acquired (corporation)',
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

with open('sample_headers.xml', 'r') as f:
    headers_string = f.read()

with open('sample_texts.xml', 'r') as f:
    texts_string = f.read()

headers_tree = etree.fromstring(headers_string)
result = [row.attrib for row in headers_tree.xpath('result/rowset/row') if row.attrib['typeID'] in selected_types.keys()]
n_type = {row['notificationID']: row['typeID'] for row in result}

texts_tree = etree.fromstring(texts_string)
for row in texts_tree.xpath('result/rowset/row'):
    id = row.attrib['notificationID']
    print selected_types[n_type[id]]
    print repr(yaml.load(row.text))
    print ''