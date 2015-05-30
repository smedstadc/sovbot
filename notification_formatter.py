from pony.orm import db_session
from models import MapDenormalize, MapSolarSystems, InvTypes

class NotificationFormatter(object):
    """Creates human readable messages from notification objects."""
    def __init__(self, names):
        self.names = names  # a mapping of strings representing character/corp/alliance ids to names.

    def format(self, notification):
        """Dispatches the appropriate message method for a given notification's typeID."""
        return self.type_handlers[notification['typeID']](self, notification)

    @staticmethod
    @db_session
    def get_system_name(notification):
        """Uses the Eve SDE to produce a solar system name from an id."""
        system_id = notification['body']['solarSystemID']
        solar_system = MapSolarSystems.get(solarSystemID=system_id)
        if solar_system:
            return solar_system.solarSystemName
        else:
            return 'unknown solar system'

    @staticmethod
    @db_session
    def get_type_name(notification):
        """Uses the Eve SDE to produce an item name from an id."""
        type_id = notification['body']['typeID']
        type = InvTypes.get(typeID=type_id)
        if type:
            return type.typeName
        else:
            return 'unknown item'

    @staticmethod
    @db_session
    def get_moon_name(notification):
        """Uses the Eve SDE to produce a planet-moon name from an id."""
        moon_id = notification['body']['moonID']
        moon = MapDenormalize.get(itemID=moon_id)
        if moon:
            return moon.itemName
        else:
            return 'unknown location'

    @staticmethod
    @db_session
    def get_planet_name(notification):
        """Uses the Eve SDE to produce a planet name from an id."""
        planet_id = notification['body']['planetID']
        planet = MapDenormalize.get(itemID=planet_id)
        if planet:
            return planet.itemName
        else:
            return 'unknown location'

    def get_name(self, name_id):
        """Gets a name from the ids to names mapping the object was initialized with."""
        name = self.names.get(str(name_id), "unknown")
        return name

    # All methods below this point produce a message string from a given notification object
    # and are dispatched to by the NotificationFormatter.format() method.
    def n38_sov_claim_fail(self, notification):
        timestamp = notification['sentDate']
        system_name = self.get_system_name(notification)
        message = "[{timestamp}] Sovereignty claim failed in {system}.".format(timestamp=timestamp, system=system_name)
        return message

    def n40_sov_bill_late(self, notification):
        timestamp = notification['sentDate']
        system_name = self.get_system_name(notification)
        message = "[{timestamp}] Sovereignty bill late for {system}.".format(timestamp=timestamp, system=system_name)
        return message

    def n42_sov_claim_lost(self, notification):
        timestamp = notification['sentDate']
        system_name = self.get_system_name(notification)
        message = "[{timestamp}] Sovereignty claim lost in {system}.".format(timestamp=timestamp, system=system_name)
        return message

    def n44_sov_claim_acquired(self, notification):
        timestamp = notification['sentDate']
        system_name = self.get_system_name(notification)
        message = "[{timestamp}] Sovereignty claim acquired in {system}.".format(timestamp=timestamp, system=system_name)
        return message

    def n45_alliance_anchoring_alert(self, notification):
        timestamp = notification['sentDate']
        alliance_name = self.get_name(notification['body']['allianceID'])
        corporation_name = self.get_name(notification['body']['corpID'])
        type_name = self.get_type_name(notification)
        system_name = self.get_system_name(notification)
        moon_name = self.get_moon_name(notification)
        message = "[{timestamp}] Control tower anchored in {system}: {type} [{alliance}] <{corp}> at {moon}."\
            .format(timestamp=timestamp, system=system_name, moon=moon_name,
                    type=type_name, alliance=alliance_name, corp=corporation_name)
        return message

    def n46_alliance_structure_vulnerable(self, notification):
        timestamp = notification['sentDate']
        system_name = self.get_system_name(notification)
        type_name = self.get_type_name(notification)
        message = "[{timestamp}] Alliance structure vulnerable: {type} in {system}."\
            .format(timestamp=timestamp, type=type_name, system=system_name)
        return message

    def n47_alliance_structure_invulnerable(self, notification):
        timestamp = notification['sentDate']
        system_name = self.get_system_name(notification)
        type_name = self.get_type_name(notification)
        message = "[{timestamp}] Alliance structure invulnerable: {type} in {system}."\
            .format(timestamp=timestamp, type=type_name, system=system_name)
        return message

    def n48_sov_disruptor_anchored(self, notification):
        timestamp = notification['sentDate']
        system_name = self.get_system_name(notification)
        message = "[{timestamp}] SBU anchored in {system}.".format(timestamp=timestamp, system=system_name)
        return message

    def n49_structure_won_lost(self, notification):
        timestamp = notification['sentDate']
        system_name = self.get_system_name(notification)
        message = "[{timestamp}] Structure won/lost in {system}: {body}"\
            .format(timestamp=timestamp, system=system_name, body=notification['body'])
        return message

    def n75_tower_alert(self, notification):
        timestamp = notification['sentDate']
        if notification['body']['moonID']:
            location_name = self.get_moon_name(notification)
        else:
            location_name = self.get_system_name(notification)
        type_name = self.get_type_name(notification)
        character_name = self.get_name(notification['body']['aggressorID'])
        corp_name = self.get_name(notification['body']['corpID'])
        alliance_name = self.get_name(notification['body']['allianceID'])
        shield_value = int(float(notification['body']['aggressorAllianceID']['shieldValue']) * 100)
        armor_value = int(float(notification['body']['aggressorAllianceID']['armorValue']) * 100)
        hull_value = int(float(notification['body']['aggressorAllianceID']['hullValue']) * 100)
        message = "[{timestamp}] Tower Alert: {type} under attack at {location}. " \
                  "Shield: {shield}%, Armor: {armor}%, Hull: {hull}%, Attacker: {character} [{alliance}] <{corp}>"\
            .format(timestamp=timestamp, type=type_name, location=location_name, shield=shield_value, armor=armor_value,
                    hull=hull_value, character=character_name, alliance=alliance_name, corp=corp_name)
        return message

    def n76_tower_resource_alert(self, notification):
        timestamp = notification['sentDate']
        location_name = self.get_moon_name(notification)
        type_name = self.get_type_name(notification)
        resource_quantity = notification['body']['wants']['quantity']
        resource_name = self.get_type_name(notification['body']['wants']['typeID'])
        message = "[{timestamp}] Tower resource alert: {type} in {location} only has {qty} {fuel}s remaining."\
            .format(timestamp=timestamp, type=type_name, location=location_name, qty=resource_quantity, fuel=resource_name)
        return message

    def n77_station_service_alert(self, notification):
        timestamp = notification['sentDate']
        system_name = self.get_system_name(notification)
        character_name = self.get_name(notification['body']['aggressorID'])
        shield_value = int(float(notification['body']['aggressorAllianceID']['shieldValue']) * 100)
        type_name = self.get_type_name(notification)
        message = "[{timestamp}] {type} under attack in {system} by {character}, shield at {shield}%.\n"\
            .format(timestamp=timestamp, type=type_name, system=system_name, character=character_name, shield=shield_value)
        return message

    def n78_station_state_change(self, notification):
        timestamp = notification['sentDate']
        message = "[{timestamp}] Station state change message: {body}".format(timestamp=timestamp, body=notification['body'])
        return message

    def n79_station_conquered(self, notification):
        timestamp = notification['sentDate']
        system_name = self.get_system_name(notification)
        character_name = self.get_name(notification['body']['aggressorID'])
        message = "[{timestamp}] Station conquered in {system} by {character}."\
            .format(timestamp=timestamp, system=system_name, character=character_name)
        return message

    def n80_station_aggression(self, notification):
        timestamp = notification['sentDate']
        system_name = self.get_system_name(notification)
        character_name = self.get_name(notification['body']['aggressorID'])
        shield_value = int(float(notification['body']['aggressorAllianceID']['shieldValue']) * 100)
        armor_value = int(float(notification['body']['aggressorAllianceID']['armorValue']) * 100)
        hull_value = int(float(notification['body']['aggressorAllianceID']['hullValue']) * 100)
        message = "[{timestamp}] Station under attack in {system}. Shield: {shield}%, Armor: " \
                  "{armor}%, Hull: {hull}%, Attacker: {character}."\
            .format(timestamp=timestamp, system=system_name, character=character_name,
                    shield=shield_value, armor=armor_value, hull=hull_value)
        return message

    def n86_tcu_under_attack(self, notification):
        timestamp = notification['sentDate']
        system_name = self.get_system_name(notification)
        character_name = self.get_name(notification['body']['aggressorID'])
        shield_value = int(float(notification['body']['shieldValue']) * 100)
        armor_value = int(float(notification['body']['armorValue']) * 100)
        hull_value = int(float(notification['body']['hullValue']) * 100)
        message = "[{timestamp}] TCU under attack in {system}. Shield: {shield}%, Armor: {armor}%, Hull: {hull}%, " \
                  "Attacker: {character}.".format(timestamp=timestamp, system=system_name, character=character_name,
                                                  shield=shield_value, armor=armor_value, hull=hull_value)
        return message

    def n87_sbu_under_attack(self, notification):
        timestamp = notification['sentDate']
        system_name = self.get_system_name(notification)
        character_name = self.get_name(notification['body']['aggressorID'])
        shield_value = int(float(notification['body']['shieldValue']) * 100)
        armor_value = int(float(notification['body']['armorValue']) * 100)
        hull_value = int(float(notification['body']['hullValue']) * 100)
        message = "[{timestamp}] SBU under attack in {system}. Shield: {shield}%, Armor: {armor}%, Hull: {hull}%, " \
                  "Attacker: {character}.".format(timestamp=timestamp, system=system_name, character=character_name,
                                                  shield=shield_value, armor=armor_value, hull=hull_value)
        return message

    def n88_ihub_under_attack(self, notification):
        timestamp = notification['sentDate']
        system_name = self.get_system_name(notification)
        character_name = self.get_name(notification['body']['aggressorID'])
        shield_value = int(float(notification['body']['shieldValue']) * 100)
        armor_value = int(float(notification['body']['armorValue']) * 100)
        hull_value = int(float(notification['body']['hullValue']) * 100)
        message = "[{timestamp}] IHUB under attack in {system}. Shield: {shield}%, Armor: {armor}%, Hull: {hull}%, " \
                  "Attacker: {character}.".format(timestamp=timestamp, system=system_name, character=character_name,
                                                  shield=shield_value, armor=armor_value, hull=hull_value)
        return message

    def n93_poco_under_attack(self, notification):
        timestamp = notification['sentDate']
        planet_name = self.get_planet_name(notification)
        character_name = self.get_name(notification['body']['aggressorID'])
        shield_value = int(float(notification['body']['aggressorAllianceID']['shieldValue']) * 100)
        armor_value = int(float(notification['body']['aggressorAllianceID']['armorValue']) * 100)
        hull_value = int(float(notification['body']['aggressorAllianceID']['hullValue']) * 100)
        message = "[{timestamp}] POCO under attack at {location}. Shield: {shield}%, Armor: {armor}%, Hull: {hull}%, " \
                  "Attacker: {character}.".format(timestamp=timestamp, location=planet_name, character=character_name,
                                                  shield=shield_value, armor=armor_value, hull=hull_value)
        return message

    def n94_poco_entered_reinforced(self, notification):
        timestamp = notification['sentDate']
        planet_name = self.get_planet_name(notification)
        message = "[{timestamp}] POCO has entered reinforced mode at {location}."\
            .format(timestamp=timestamp, location=planet_name)
        return message

    # Maps notification typeIDs to the method that handles message creation for that type.
    type_handlers = {'38': n38_sov_claim_fail,
                     '40': n40_sov_bill_late,
                     '42': n42_sov_claim_lost,
                     '44': n44_sov_claim_acquired,
                     '45': n45_alliance_anchoring_alert,
                     '46': n46_alliance_structure_vulnerable,
                     '47': n47_alliance_structure_invulnerable,
                     '48': n48_sov_disruptor_anchored,
                     '49': n49_structure_won_lost,
                     '75': n75_tower_alert,
                     '76': n76_tower_resource_alert,
                     '77': n77_station_service_alert,
                     '78': n78_station_state_change,
                     '79': n79_station_conquered,
                     '80': n80_station_aggression,
                     '86': n86_tcu_under_attack,
                     '87': n87_sbu_under_attack,
                     '88': n88_ihub_under_attack,
                     '93': n93_poco_under_attack,
                     '94': n94_poco_entered_reinforced}
