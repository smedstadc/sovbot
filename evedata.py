"""This module creates pony orm mappings for the tables and columns that will be used."""

from pony.orm import *

db = Database()
db.bind('sqlite', 'sqlite-latest.sqlite')


class InvTypes(db.Entity):
    _table_ = 'invTypes'
    typeID = PrimaryKey(int)
    typeName = Required(unicode)


class MapDenormalize(db.Entity):
    _table_ = 'mapDenormalize'
    itemID = PrimaryKey(int)
    itemName = Required(unicode)
    solarSystemID = Required(int)


class Stations(db.Entity):
    _table_ = 'staStations'
    stationID = PrimaryKey(int)
    stationName = Required(unicode)


db.generate_mapping()
# quick sanity check demo
if __name__ == "__main__":
    with db_session:
        items = select(item for item in InvTypes if item.typeID in [34, 35, 36, 37])
        for dat in items:
            print dat.typeName, dat.typeID
        map_item = MapDenormalize.get(itemID='40009081')
        print map_item.itemName
