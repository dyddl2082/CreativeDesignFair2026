# generated from rosidl_generator_py/resource/_idl.py.em
# with input from macrobot_interfaces:msg/DepthCandidateArray.idl
# generated code does not contain a copyright notice

# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
from os import getenv

ros_python_check_fields = getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

# Member 'plane_coefficients'
import numpy  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_DepthCandidateArray(type):
    """Metaclass of message 'DepthCandidateArray'."""

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
                'macrobot_interfaces.msg.DepthCandidateArray')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__depth_candidate_array
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__depth_candidate_array
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__depth_candidate_array
            cls._TYPE_SUPPORT = module.type_support_msg__msg__depth_candidate_array
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__depth_candidate_array

            from macrobot_interfaces.msg import DepthCandidate
            if DepthCandidate.__class__._TYPE_SUPPORT is None:
                DepthCandidate.__class__.__import_type_support__()

            from sensor_msgs.msg import CompressedImage
            if CompressedImage.__class__._TYPE_SUPPORT is None:
                CompressedImage.__class__.__import_type_support__()

            from std_msgs.msg import Header
            if Header.__class__._TYPE_SUPPORT is None:
                Header.__class__.__import_type_support__()

    @classmethod
    def __prepare__(cls, name, bases, **kwargs):
        # list constant names here so that they appear in the help text of
        # the message class under "Data and other attributes defined here:"
        # as well as populate each message instance
        return {
        }


class DepthCandidateArray(metaclass=Metaclass_DepthCandidateArray):
    """Message class 'DepthCandidateArray'."""

    __slots__ = [
        '_header',
        '_image_width',
        '_image_height',
        '_plane_found',
        '_plane_inlier_ratio',
        '_plane_coefficients',
        '_foreground_mask_available',
        '_foreground_mask',
        '_candidates',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'image_width': 'uint32',
        'image_height': 'uint32',
        'plane_found': 'boolean',
        'plane_inlier_ratio': 'float',
        'plane_coefficients': 'float[4]',
        'foreground_mask_available': 'boolean',
        'foreground_mask': 'sensor_msgs/CompressedImage',
        'candidates': 'sequence<macrobot_interfaces/DepthCandidate>',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.Array(rosidl_parser.definition.BasicType('float'), 4),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['sensor_msgs', 'msg'], 'CompressedImage'),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.NamespacedType(['macrobot_interfaces', 'msg'], 'DepthCandidate')),  # noqa: E501
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
        from std_msgs.msg import Header
        self.header = kwargs.get('header', Header())
        self.image_width = kwargs.get('image_width', int())
        self.image_height = kwargs.get('image_height', int())
        self.plane_found = kwargs.get('plane_found', bool())
        self.plane_inlier_ratio = kwargs.get('plane_inlier_ratio', float())
        if 'plane_coefficients' not in kwargs:
            self.plane_coefficients = numpy.zeros(4, dtype=numpy.float32)
        else:
            self.plane_coefficients = kwargs.get('plane_coefficients')
        self.foreground_mask_available = kwargs.get('foreground_mask_available', bool())
        from sensor_msgs.msg import CompressedImage
        self.foreground_mask = kwargs.get('foreground_mask', CompressedImage())
        self.candidates = kwargs.get('candidates', [])

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
        if self.header != other.header:
            return False
        if self.image_width != other.image_width:
            return False
        if self.image_height != other.image_height:
            return False
        if self.plane_found != other.plane_found:
            return False
        if self.plane_inlier_ratio != other.plane_inlier_ratio:
            return False
        if any(self.plane_coefficients != other.plane_coefficients):
            return False
        if self.foreground_mask_available != other.foreground_mask_available:
            return False
        if self.foreground_mask != other.foreground_mask:
            return False
        if self.candidates != other.candidates:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def header(self):
        """Message field 'header'."""
        return self._header

    @header.setter
    def header(self, value):
        if self._check_fields:
            from std_msgs.msg import Header
            assert \
                isinstance(value, Header), \
                "The 'header' field must be a sub message of type 'Header'"
        self._header = value

    @builtins.property
    def image_width(self):
        """Message field 'image_width'."""
        return self._image_width

    @image_width.setter
    def image_width(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'image_width' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'image_width' field must be an unsigned integer in [0, 4294967295]"
        self._image_width = value

    @builtins.property
    def image_height(self):
        """Message field 'image_height'."""
        return self._image_height

    @image_height.setter
    def image_height(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'image_height' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'image_height' field must be an unsigned integer in [0, 4294967295]"
        self._image_height = value

    @builtins.property
    def plane_found(self):
        """Message field 'plane_found'."""
        return self._plane_found

    @plane_found.setter
    def plane_found(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'plane_found' field must be of type 'bool'"
        self._plane_found = value

    @builtins.property
    def plane_inlier_ratio(self):
        """Message field 'plane_inlier_ratio'."""
        return self._plane_inlier_ratio

    @plane_inlier_ratio.setter
    def plane_inlier_ratio(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'plane_inlier_ratio' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'plane_inlier_ratio' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._plane_inlier_ratio = value

    @builtins.property
    def plane_coefficients(self):
        """Message field 'plane_coefficients'."""
        return self._plane_coefficients

    @plane_coefficients.setter
    def plane_coefficients(self, value):
        if self._check_fields:
            if isinstance(value, numpy.ndarray):
                assert value.dtype == numpy.float32, \
                    "The 'plane_coefficients' numpy.ndarray() must have the dtype of 'numpy.float32'"
                assert value.size == 4, \
                    "The 'plane_coefficients' numpy.ndarray() must have a size of 4"
                self._plane_coefficients = value
                return
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 len(value) == 4 and
                 all(isinstance(v, float) for v in value) and
                 all(not (val < -3.402823466e+38 or val > 3.402823466e+38) or math.isinf(val) for val in value)), \
                "The 'plane_coefficients' field must be a set or sequence with length 4 and each value of type 'float' and each float in [-340282346600000016151267322115014000640.000000, 340282346600000016151267322115014000640.000000]"
        self._plane_coefficients = numpy.array(value, dtype=numpy.float32)

    @builtins.property
    def foreground_mask_available(self):
        """Message field 'foreground_mask_available'."""
        return self._foreground_mask_available

    @foreground_mask_available.setter
    def foreground_mask_available(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'foreground_mask_available' field must be of type 'bool'"
        self._foreground_mask_available = value

    @builtins.property
    def foreground_mask(self):
        """Message field 'foreground_mask'."""
        return self._foreground_mask

    @foreground_mask.setter
    def foreground_mask(self, value):
        if self._check_fields:
            from sensor_msgs.msg import CompressedImage
            assert \
                isinstance(value, CompressedImage), \
                "The 'foreground_mask' field must be a sub message of type 'CompressedImage'"
        self._foreground_mask = value

    @builtins.property
    def candidates(self):
        """Message field 'candidates'."""
        return self._candidates

    @candidates.setter
    def candidates(self, value):
        if self._check_fields:
            from macrobot_interfaces.msg import DepthCandidate
            from collections.abc import Sequence
            from collections.abc import Set
            from collections import UserList
            from collections import UserString
            assert \
                ((isinstance(value, Sequence) or
                  isinstance(value, Set) or
                  isinstance(value, UserList)) and
                 not isinstance(value, str) and
                 not isinstance(value, UserString) and
                 all(isinstance(v, DepthCandidate) for v in value) and
                 True), \
                "The 'candidates' field must be a set or sequence and each value of type 'DepthCandidate'"
        self._candidates = value
