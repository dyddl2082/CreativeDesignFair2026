# generated from rosidl_generator_py/resource/_idl.py.em
# with input from macrobot_interfaces:msg/DepthCandidate.idl
# generated code does not contain a copyright notice

# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
from os import getenv

ros_python_check_fields = getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_DepthCandidate(type):
    """Metaclass of message 'DepthCandidate'."""

    _CREATE_ROS_MESSAGE = None
    _CONVERT_FROM_PY = None
    _CONVERT_TO_PY = None
    _DESTROY_ROS_MESSAGE = None
    _TYPE_SUPPORT = None

    __constants = {
    }

    @classmethod
    def __import_type_support__(cls):
        try:
            from rosidl_generator_py import import_type_support
            module = import_type_support('macrobot_interfaces')
        except ImportError:
            import logging
            import traceback
            logger = logging.getLogger(
                'macrobot_interfaces.msg.DepthCandidate')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__depth_candidate
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__depth_candidate
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__depth_candidate
            cls._TYPE_SUPPORT = module.type_support_msg__msg__depth_candidate
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__depth_candidate

            from sensor_msgs.msg import RegionOfInterest
            if RegionOfInterest.__class__._TYPE_SUPPORT is None:
                RegionOfInterest.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class DepthCandidate(metaclass=Metaclass_DepthCandidate):
    """Message class 'DepthCandidate'."""

    __slots__ = [
        '_id',
        '_roi',
        '_center_x',
        '_center_y',
        '_median_depth_m',
        '_near_depth_m',
        '_far_depth_m',
        '_depth_std_m',
        '_valid_depth_ratio',
        '_fill_ratio',
        '_area_ratio',
        '_foreground_height_m',
        '_foreground_height_valid',
        '_proposal_score',
        '_touches_border',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'id': 'uint32',
        'roi': 'sensor_msgs/RegionOfInterest',
        'center_x': 'float',
        'center_y': 'float',
        'median_depth_m': 'float',
        'near_depth_m': 'float',
        'far_depth_m': 'float',
        'depth_std_m': 'float',
        'valid_depth_ratio': 'float',
        'fill_ratio': 'float',
        'area_ratio': 'float',
        'foreground_height_m': 'float',
        'foreground_height_valid': 'boolean',
        'proposal_score': 'float',
        'touches_border': 'boolean',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['sensor_msgs', 'msg'], 'RegionOfInterest'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
    )

    def __init__(self, **kwargs):
        if 'check_fields' in kwargs:
            self._check_fields = kwargs['check_fields']
        else:
            self._check_fields = ros_python_check_fields == '1'
        if self._check_fields:
            assert all('_' + key in self.__slots__ for key in kwargs.keys()), \
                'Invalid arguments passed to constructor: %s' % \
                ', '.join(sorted(k for k in kwargs.keys() if '_' + k not in self.__slots__))
        self.id = kwargs.get('id', int())
        from sensor_msgs.msg import RegionOfInterest
        self.roi = kwargs.get('roi', RegionOfInterest())
        self.center_x = kwargs.get('center_x', float())
        self.center_y = kwargs.get('center_y', float())
        self.median_depth_m = kwargs.get('median_depth_m', float())
        self.near_depth_m = kwargs.get('near_depth_m', float())
        self.far_depth_m = kwargs.get('far_depth_m', float())
        self.depth_std_m = kwargs.get('depth_std_m', float())
        self.valid_depth_ratio = kwargs.get('valid_depth_ratio', float())
        self.fill_ratio = kwargs.get('fill_ratio', float())
        self.area_ratio = kwargs.get('area_ratio', float())
        self.foreground_height_m = kwargs.get('foreground_height_m', float())
        self.foreground_height_valid = kwargs.get('foreground_height_valid', bool())
        self.proposal_score = kwargs.get('proposal_score', float())
        self.touches_border = kwargs.get('touches_border', bool())

    def __repr__(self):
        typename = self.__class__.__module__.split('.')
        typename.pop()
        typename.append(self.__class__.__name__)
        args = []
        for s, t in zip(self.get_fields_and_field_types().keys(), self.SLOT_TYPES):
            field = getattr(self, s)
            fieldstr = repr(field)
            # We use Python array type for fields that can be directly stored
            # in them, and "normal" sequences for everything else.  If it is
            # a type that we store in an array, strip off the 'array' portion.
            if (
                isinstance(t, rosidl_parser.definition.AbstractSequence) and
                isinstance(t.value_type, rosidl_parser.definition.BasicType) and
                t.value_type.typename in ['float', 'double', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64']
            ):
                if len(field) == 0:
                    fieldstr = '[]'
                else:
                    if self._check_fields:
                        assert fieldstr.startswith('array(')
                    prefix = "array('X', "
                    suffix = ')'
                    fieldstr = fieldstr[len(prefix):-len(suffix)]
            args.append(s + '=' + fieldstr)
        return '%s(%s)' % ('.'.join(typename), ', '.join(args))

    def __eq__(self, other):
        if not isinstance(other, self.__class__):
            return False
        if self.id != other.id:
            return False
        if self.roi != other.roi:
            return False
        if self.center_x != other.center_x:
            return False
        if self.center_y != other.center_y:
            return False
        if self.median_depth_m != other.median_depth_m:
            return False
        if self.near_depth_m != other.near_depth_m:
            return False
        if self.far_depth_m != other.far_depth_m:
            return False
        if self.depth_std_m != other.depth_std_m:
            return False
        if self.valid_depth_ratio != other.valid_depth_ratio:
            return False
        if self.fill_ratio != other.fill_ratio:
            return False
        if self.area_ratio != other.area_ratio:
            return False
        if self.foreground_height_m != other.foreground_height_m:
            return False
        if self.foreground_height_valid != other.foreground_height_valid:
            return False
        if self.proposal_score != other.proposal_score:
            return False
        if self.touches_border != other.touches_border:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property  # noqa: A003
    def id(self):  # noqa: A003
        """Message field 'id'."""
        return self._id

    @id.setter  # noqa: A003
    def id(self, value):  # noqa: A003
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'id' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'id' field must be an unsigned integer in [0, 4294967295]"
        self._id = value

    @builtins.property
    def roi(self):
        """Message field 'roi'."""
        return self._roi

    @roi.setter
    def roi(self, value):
        if self._check_fields:
            from sensor_msgs.msg import RegionOfInterest
            assert \
                isinstance(value, RegionOfInterest), \
                "The 'roi' field must be a sub message of type 'RegionOfInterest'"
        self._roi = value

    @builtins.property
    def center_x(self):
        """Message field 'center_x'."""
        return self._center_x

    @center_x.setter
    def center_x(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'center_x' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'center_x' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._center_x = value

    @builtins.property
    def center_y(self):
        """Message field 'center_y'."""
        return self._center_y

    @center_y.setter
    def center_y(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'center_y' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'center_y' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._center_y = value

    @builtins.property
    def median_depth_m(self):
        """Message field 'median_depth_m'."""
        return self._median_depth_m

    @median_depth_m.setter
    def median_depth_m(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'median_depth_m' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'median_depth_m' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._median_depth_m = value

    @builtins.property
    def near_depth_m(self):
        """Message field 'near_depth_m'."""
        return self._near_depth_m

    @near_depth_m.setter
    def near_depth_m(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'near_depth_m' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'near_depth_m' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._near_depth_m = value

    @builtins.property
    def far_depth_m(self):
        """Message field 'far_depth_m'."""
        return self._far_depth_m

    @far_depth_m.setter
    def far_depth_m(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'far_depth_m' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'far_depth_m' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._far_depth_m = value

    @builtins.property
    def depth_std_m(self):
        """Message field 'depth_std_m'."""
        return self._depth_std_m

    @depth_std_m.setter
    def depth_std_m(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'depth_std_m' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'depth_std_m' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._depth_std_m = value

    @builtins.property
    def valid_depth_ratio(self):
        """Message field 'valid_depth_ratio'."""
        return self._valid_depth_ratio

    @valid_depth_ratio.setter
    def valid_depth_ratio(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'valid_depth_ratio' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'valid_depth_ratio' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._valid_depth_ratio = value

    @builtins.property
    def fill_ratio(self):
        """Message field 'fill_ratio'."""
        return self._fill_ratio

    @fill_ratio.setter
    def fill_ratio(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'fill_ratio' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'fill_ratio' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._fill_ratio = value

    @builtins.property
    def area_ratio(self):
        """Message field 'area_ratio'."""
        return self._area_ratio

    @area_ratio.setter
    def area_ratio(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'area_ratio' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'area_ratio' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._area_ratio = value

    @builtins.property
    def foreground_height_m(self):
        """Message field 'foreground_height_m'."""
        return self._foreground_height_m

    @foreground_height_m.setter
    def foreground_height_m(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'foreground_height_m' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'foreground_height_m' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._foreground_height_m = value

    @builtins.property
    def foreground_height_valid(self):
        """Message field 'foreground_height_valid'."""
        return self._foreground_height_valid

    @foreground_height_valid.setter
    def foreground_height_valid(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'foreground_height_valid' field must be of type 'bool'"
        self._foreground_height_valid = value

    @builtins.property
    def proposal_score(self):
        """Message field 'proposal_score'."""
        return self._proposal_score

    @proposal_score.setter
    def proposal_score(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'proposal_score' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'proposal_score' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._proposal_score = value

    @builtins.property
    def touches_border(self):
        """Message field 'touches_border'."""
        return self._touches_border

    @touches_border.setter
    def touches_border(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'touches_border' field must be of type 'bool'"
        self._touches_border = value
