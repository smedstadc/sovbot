import os
from pony.orm import *

###############
# Sovbot Data #
###############
database_path = os.path.join(os.path.dirname(__file__), 'sovbot.sqlite')
sovbot_db = Database("sqlite", database_path, create_db=True)

class Notification(sovbot_db.Entity):
    """Pony ORM model for Notification Headers"""
    id = PrimaryKey(int, auto=False)
    type_id = Required(int)
    read = Required(bool)
    sender_id = Required(int)
    sent_date = Required(unicode)
    sender_name = Required(unicode)

sovbot_db.generate_mapping(create_tables=True)


######################################
# Mappings to Eve Static Data Export #
######################################
eve_sde = Database()
eve_sde.bind('sqlite', os.path.join(os.path.dirname(__file__), 'sqlite-latest.sqlite'))

class InvTypes(eve_sde.Entity):
    _table_ = 'invTypes'
    typeID = PrimaryKey(int)
    typeName = Required(unicode)

class MapSolarSystems(eve_sde.Entity):
    _table_ = 'mapSolarSystems'
    solarSystemID = PrimaryKey(int)
    solarSystemName = Required(unicode)

class MapDenormalize(eve_sde.Entity):
    _table_ = 'mapDenormalize'
    itemID = PrimaryKey(int)
    itemName = Required(unicode)


class Stations(eve_sde.Entity):
    _table_ = 'staStations'
    stationID = PrimaryKey(int)
    stationName = Required(unicode)


eve_sde.generate_mapping()

if __name__ == "__main__":
    # quick sanity check demo
    with db_session:
        items = select(item for item in InvTypes if item.typeID in [34, 35, 36, 37])
        for dat in items:
            print dat.typeName, dat.typeID
        map_item = MapDenormalize.get(itemID='40009081')
        print map_item.itemName