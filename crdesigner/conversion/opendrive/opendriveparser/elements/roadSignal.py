# -*- coding: utf-8 -*-

class Signal:

    def __init__(self):
        self._s = None
        self._t = None
        self._id = None
        self._name = None
        self._dynamic = None
        self._orientation = None
        self._type = None
        self._subtype = None
        self._country = None
        self._signalvalue = None
        self._unit = None
        self._text = None

        """
        ###not supported in CommonRoad Signs/Lights###
        #self._zOffset = None
        #self._countryRevision = None
        
        self._height = None
        self._width = None
        self._hOffset = None
        self._pitch = None
        self._roll = None
        
        """

    @property
    def s(self):
        return self._s

    @s.setter
    def s(self, value):
        self._s = float(value)

    @property
    def t(self):
        return self._t

    @t.setter
    def t(self, value):
        self._t = float(value)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = int(value)

    @property
    def name(self):
        return self._name

    @name.setter
    def name(self, value):
        self._name = str(value)

    @property
    def dynamic(self):
        return self._dynamic

    @dynamic.setter
    def dynamic(self, value):
        self._dynamic = str(value)

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, value):
        self._orientation = str(value)

    @property
    def country(self):
        return self._country

    @country.setter
    def country(self, value):
        self._country = str(value)

    @property
    def signalvalue(self):
        return self._signalvalue

    @signalvalue.setter
    def value(self, value):
        self._signalvalue = float(value)

    @property
    def unit(self):
        return self._unit

    @unit.setter
    def unit(self, value):
        self._unit = str(value)

    @property
    def text(self):
        return self._text

    @text.setter
    def text(self, value):
        self._text = str(value)

    @signalvalue.setter
    def signalvalue(self, value):
        self._signalvalue = value

    @property
    def type(self):
        return self._type

    @type.setter
    def type(self, value):
        self._type = str(value)

    @property
    def subtype(self):
        return self._subtype

    @subtype.setter
    def subtype(self, value):
        self._subtype = int(value)


class SignalReference:
    """
    In OpenDRIVE, a reference to another signal for reuse of signal information
    is represented by the <signalReference> element within the <signal> element.

    attributes  name        type    unit    value       Description
                x           double     m    ]-∞;∞[      x-coordinate
                y           double     m    ]-∞;∞[      y-coordinate
                id          string                      Unique ID of the referenced signal within the database
                orientation e_orientation   +; -; none  "+" = valid in positive s- direction
                                                        "-" = valid in negative s- direction
                                                        "none" = valid in both directions

    Rules:
    The following rules apply for the purpose of reusing signal information:
    A lane validity element may be added for every <signalReference> element.
    Signal reference shall be used for signals only.
    For the signal that reuses the content of another signal, the direction for which it is valid shall be specified.
    """
    def __init__(self):
        self._s = None
        self._t = None
        self._id = None
        self._orientation = None

    @property
    def s(self):
        return self._s

    @s.setter
    def s(self, value):
        self._s = float(value)

    @property
    def t(self):
        return self._t

    @t.setter
    def t(self, value):
        self._t = float(value)

    @property
    def id(self):
        return self._id

    @id.setter
    def id(self, value):
        self._id = int(value)

    @property
    def orientation(self):
        return self._orientation

    @orientation.setter
    def orientation(self, value):
        self._orientation = str(value)