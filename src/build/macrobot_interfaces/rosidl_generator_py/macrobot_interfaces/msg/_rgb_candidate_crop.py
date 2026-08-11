# generated from rosidl_generator_py/resource/_idl.py.em
# with input from macrobot_interfaces:msg/RgbCandidateCrop.idl
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


class Metaclass_RgbCandidateCrop(type):
    """Metaclass of message 'RgbCandidateCrop'."""

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
                'macrobot_interfaces.msg.RgbCandidateCrop')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__rgb_candidate_crop
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__rgb_candidate_crop
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__rgb_candidate_crop
            cls._TYPE_SUPPORT = module.type_support_msg__msg__rgb_candidate_crop
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__rgb_candidate_crop

            from macrobot_interfaces.msg import DepthCandidate
            if DepthCandidate.__class__._TYPE_SUPPORT is None:
                DepthCandidate.__class__.__import_type_support__()

            from sensor_msgs.msg import CompressedImage
            if CompressedImage.__class__._TYPE_SUPPORT is None:
                CompressedImage.__class__.__import_type_support__()

            from sensor_msgs.msg import RegionOfInterest
            if RegionOfInterest.__class__._TYPE_SUPPORT is None:
                RegionOfInterest.__class__.__import_type_support__()

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


class RgbCandidateCrop(metaclass=Metaclass_RgbCandidateCrop):
    """Message class 'RgbCandidateCrop'."""

    __slots__ = [
        '_proposal_header',
        '_proposal_image_width',
        '_proposal_image_height',
        '_color_image_width',
        '_color_image_height',
        '_source_candidate_count',
        '_frame_crop_count',
        '_crop_index',
        '_candidate',
        '_crop_roi',
        '_color_time_offset_sec',
        '_plane_found',
        '_foreground_mask_available',
        '_mask_fill_ratio',
        '_foreground_mask',
        '_encoded_width',
        '_encoded_height',
        '_jpeg_size_bytes',
        '_jpeg_quality',
        '_size_limit_met',
        '_image',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'proposal_header': 'std_msgs/Header',
        'proposal_image_width': 'uint32',
        'proposal_image_height': 'uint32',
        'color_image_width': 'uint32',
        'color_image_height': 'uint32',
        'source_candidate_count': 'uint32',
        'frame_crop_count': 'uint32',
        'crop_index': 'uint32',
        'candidate': 'macrobot_interfaces/DepthCandidate',
        'crop_roi': 'sensor_msgs/RegionOfInterest',
        'color_time_offset_sec': 'float',
        'plane_found': 'boolean',
        'foreground_mask_available': 'boolean',
        'mask_fill_ratio': 'float',
        'foreground_mask': 'sensor_msgs/CompressedImage',
        'encoded_width': 'uint32',
        'encoded_height': 'uint32',
        'jpeg_size_bytes': 'uint32',
        'jpeg_quality': 'uint8',
        'size_limit_met': 'boolean',
        'image': 'sensor_msgs/CompressedImage',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['macrobot_interfaces', 'msg'], 'DepthCandidate'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['sensor_msgs', 'msg'], 'RegionOfInterest'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['sensor_msgs', 'msg'], 'CompressedImage'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint8'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['sensor_msgs', 'msg'], 'CompressedImage'),  # noqa: E501
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
        self.proposal_header = kwargs.get('proposal_header', Header())
        self.proposal_image_width = kwargs.get('proposal_image_width', int())
        self.proposal_image_height = kwargs.get('proposal_image_height', int())
        self.color_image_width = kwargs.get('color_image_width', int())
        self.color_image_height = kwargs.get('color_image_height', int())
        self.source_candidate_count = kwargs.get('source_candidate_count', int())
        self.frame_crop_count = kwargs.get('frame_crop_count', int())
        self.crop_index = kwargs.get('crop_index', int())
        from macrobot_interfaces.msg import DepthCandidate
        self.candidate = kwargs.get('candidate', DepthCandidate())
        from sensor_msgs.msg import RegionOfInterest
        self.crop_roi = kwargs.get('crop_roi', RegionOfInterest())
        self.color_time_offset_sec = kwargs.get('color_time_offset_sec', float())
        self.plane_found = kwargs.get('plane_found', bool())
        self.foreground_mask_available = kwargs.get('foreground_mask_available', bool())
        self.mask_fill_ratio = kwargs.get('mask_fill_ratio', float())
        from sensor_msgs.msg import CompressedImage
        self.foreground_mask = kwargs.get('foreground_mask', CompressedImage())
        self.encoded_width = kwargs.get('encoded_width', int())
        self.encoded_height = kwargs.get('encoded_height', int())
        self.jpeg_size_bytes = kwargs.get('jpeg_size_bytes', int())
        self.jpeg_quality = kwargs.get('jpeg_quality', int())
        self.size_limit_met = kwargs.get('size_limit_met', bool())
        from sensor_msgs.msg import CompressedImage
        self.image = kwargs.get('image', CompressedImage())

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
        if self.proposal_header != other.proposal_header:
            return False
        if self.proposal_image_width != other.proposal_image_width:
            return False
        if self.proposal_image_height != other.proposal_image_height:
            return False
        if self.color_image_width != other.color_image_width:
            return False
        if self.color_image_height != other.color_image_height:
            return False
        if self.source_candidate_count != other.source_candidate_count:
            return False
        if self.frame_crop_count != other.frame_crop_count:
            return False
        if self.crop_index != other.crop_index:
            return False
        if self.candidate != other.candidate:
            return False
        if self.crop_roi != other.crop_roi:
            return False
        if self.color_time_offset_sec != other.color_time_offset_sec:
            return False
        if self.plane_found != other.plane_found:
            return False
        if self.foreground_mask_available != other.foreground_mask_available:
            return False
        if self.mask_fill_ratio != other.mask_fill_ratio:
            return False
        if self.foreground_mask != other.foreground_mask:
            return False
        if self.encoded_width != other.encoded_width:
            return False
        if self.encoded_height != other.encoded_height:
            return False
        if self.jpeg_size_bytes != other.jpeg_size_bytes:
            return False
        if self.jpeg_quality != other.jpeg_quality:
            return False
        if self.size_limit_met != other.size_limit_met:
            return False
        if self.image != other.image:
            return False
        return True

    @classmethod
    def get_fields_and_field_types(cls):
        from copy import copy
        return copy(cls._fields_and_field_types)

    @builtins.property
    def proposal_header(self):
        """Message field 'proposal_header'."""
        return self._proposal_header

    @proposal_header.setter
    def proposal_header(self, value):
        if self._check_fields:
            from std_msgs.msg import Header
            assert \
                isinstance(value, Header), \
                "The 'proposal_header' field must be a sub message of type 'Header'"
        self._proposal_header = value

    @builtins.property
    def proposal_image_width(self):
        """Message field 'proposal_image_width'."""
        return self._proposal_image_width

    @proposal_image_width.setter
    def proposal_image_width(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'proposal_image_width' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'proposal_image_width' field must be an unsigned integer in [0, 4294967295]"
        self._proposal_image_width = value

    @builtins.property
    def proposal_image_height(self):
        """Message field 'proposal_image_height'."""
        return self._proposal_image_height

    @proposal_image_height.setter
    def proposal_image_height(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'proposal_image_height' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'proposal_image_height' field must be an unsigned integer in [0, 4294967295]"
        self._proposal_image_height = value

    @builtins.property
    def color_image_width(self):
        """Message field 'color_image_width'."""
        return self._color_image_width

    @color_image_width.setter
    def color_image_width(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'color_image_width' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'color_image_width' field must be an unsigned integer in [0, 4294967295]"
        self._color_image_width = value

    @builtins.property
    def color_image_height(self):
        """Message field 'color_image_height'."""
        return self._color_image_height

    @color_image_height.setter
    def color_image_height(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'color_image_height' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'color_image_height' field must be an unsigned integer in [0, 4294967295]"
        self._color_image_height = value

    @builtins.property
    def source_candidate_count(self):
        """Message field 'source_candidate_count'."""
        return self._source_candidate_count

    @source_candidate_count.setter
    def source_candidate_count(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'source_candidate_count' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'source_candidate_count' field must be an unsigned integer in [0, 4294967295]"
        self._source_candidate_count = value

    @builtins.property
    def frame_crop_count(self):
        """Message field 'frame_crop_count'."""
        return self._frame_crop_count

    @frame_crop_count.setter
    def frame_crop_count(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'frame_crop_count' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'frame_crop_count' field must be an unsigned integer in [0, 4294967295]"
        self._frame_crop_count = value

    @builtins.property
    def crop_index(self):
        """Message field 'crop_index'."""
        return self._crop_index

    @crop_index.setter
    def crop_index(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'crop_index' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'crop_index' field must be an unsigned integer in [0, 4294967295]"
        self._crop_index = value

    @builtins.property
    def candidate(self):
        """Message field 'candidate'."""
        return self._candidate

    @candidate.setter
    def candidate(self, value):
        if self._check_fields:
            from macrobot_interfaces.msg import DepthCandidate
            assert \
                isinstance(value, DepthCandidate), \
                "The 'candidate' field must be a sub message of type 'DepthCandidate'"
        self._candidate = value

    @builtins.property
    def crop_roi(self):
        """Message field 'crop_roi'."""
        return self._crop_roi

    @crop_roi.setter
    def crop_roi(self, value):
        if self._check_fields:
            from sensor_msgs.msg import RegionOfInterest
            assert \
                isinstance(value, RegionOfInterest), \
                "The 'crop_roi' field must be a sub message of type 'RegionOfInterest'"
        self._crop_roi = value

    @builtins.property
    def color_time_offset_sec(self):
        """Message field 'color_time_offset_sec'."""
        return self._color_time_offset_sec

    @color_time_offset_sec.setter
    def color_time_offset_sec(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'color_time_offset_sec' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'color_time_offset_sec' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._color_time_offset_sec = value

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
    def mask_fill_ratio(self):
        """Message field 'mask_fill_ratio'."""
        return self._mask_fill_ratio

    @mask_fill_ratio.setter
    def mask_fill_ratio(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'mask_fill_ratio' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'mask_fill_ratio' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._mask_fill_ratio = value

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
    def encoded_width(self):
        """Message field 'encoded_width'."""
        return self._encoded_width

    @encoded_width.setter
    def encoded_width(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'encoded_width' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'encoded_width' field must be an unsigned integer in [0, 4294967295]"
        self._encoded_width = value

    @builtins.property
    def encoded_height(self):
        """Message field 'encoded_height'."""
        return self._encoded_height

    @encoded_height.setter
    def encoded_height(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'encoded_height' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'encoded_height' field must be an unsigned integer in [0, 4294967295]"
        self._encoded_height = value

    @builtins.property
    def jpeg_size_bytes(self):
        """Message field 'jpeg_size_bytes'."""
        return self._jpeg_size_bytes

    @jpeg_size_bytes.setter
    def jpeg_size_bytes(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'jpeg_size_bytes' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'jpeg_size_bytes' field must be an unsigned integer in [0, 4294967295]"
        self._jpeg_size_bytes = value

    @builtins.property
    def jpeg_quality(self):
        """Message field 'jpeg_quality'."""
        return self._jpeg_quality

    @jpeg_quality.setter
    def jpeg_quality(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'jpeg_quality' field must be of type 'int'"
            assert value >= 0 and value < 256, \
                "The 'jpeg_quality' field must be an unsigned integer in [0, 255]"
        self._jpeg_quality = value

    @builtins.property
    def size_limit_met(self):
        """Message field 'size_limit_met'."""
        return self._size_limit_met

    @size_limit_met.setter
    def size_limit_met(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'size_limit_met' field must be of type 'bool'"
        self._size_limit_met = value

    @builtins.property
    def image(self):
        """Message field 'image'."""
        return self._image

    @image.setter
    def image(self, value):
        if self._check_fields:
            from sensor_msgs.msg import CompressedImage
            assert \
                isinstance(value, CompressedImage), \
                "The 'image' field must be a sub message of type 'CompressedImage'"
        self._image = value
