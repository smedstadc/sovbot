import os
import pony.orm

database_path = os.path.join(os.path.dirname(__file__), 'sovbot.sqlite')
db = pony.orm.Database("sqlite", database_path, create_db=True)

class Notification(db.Entity):
    """Pony ORM model for Notification Headers"""
    id = pony.orm.PrimaryKey(int, auto=False)
    type_id = pony.orm.Required(int)
    read = pony.orm.Required(bool)
    sender_id = pony.orm.Required(int)
    sent_date = pony.orm.Required(unicode)
    sender_name = pony.orm.Required(unicode)

db.generate_mapping(create_tables=True)
