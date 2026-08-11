# generated from rosidl_generator_py/resource/_idl.py.em
# with input from macrobot_interfaces:msg/CandidateFilterResult.idl
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


class Metaclass_CandidateFilterResult(type):
    """Metaclass of message 'CandidateFilterResult'."""

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
                'macrobot_interfaces.msg.CandidateFilterResult')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__candidate_filter_result
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__candidate_filter_result
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__candidate_filter_result
            cls._TYPE_SUPPORT = module.type_support_msg__msg__candidate_filter_result
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__candidate_filter_result

            from macrobot_interfaces.msg import DepthCandidate
            if DepthCandidate.__class__._TYPE_SUPPORT is None:
                DepthCandidate.__class__.__import_type_support__()

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


class CandidateFilterResult(metaclass=Metaclass_CandidateFilterResult):
    """Message class 'CandidateFilterResult'."""

    __slots__ = [
        '_proposal_header',
        '_image_header',
        '_candidate_id',
        '_crop_index',
        '_frame_crop_count',
        '_target_object',
        '_reference_profile_available',
        '_reference_image_count',
        '_camera_info_available',
        '_plane_found',
        '_foreground_height_valid',
        '_foreground_mask_available',
        '_accepted',
        '_reject_stage',
        '_reject_reason',
        '_objectness_score',
        '_target_hint_score',
        '_filter_score',
        '_depth_score',
        '_quality_score',
        '_color_score',
        '_shape_score',
        '_physical_size_score',
        '_sharpness',
        '_mean_brightness',
        '_dark_ratio',
        '_bright_clip_ratio',
        '_edge_density',
        '_mask_fill_ratio',
        '_mask_solidity',
        '_color_similarity',
        '_aspect_ratio',
        '_estimated_width_m',
        '_estimated_height_m',
        '_sync_offset_abs_sec',
        '_candidate',
        '_crop_roi',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'proposal_header': 'std_msgs/Header',
        'image_header': 'std_msgs/Header',
        'candidate_id': 'uint32',
        'crop_index': 'uint32',
        'frame_crop_count': 'uint32',
        'target_object': 'string',
        'reference_profile_available': 'boolean',
        'reference_image_count': 'uint32',
        'camera_info_available': 'boolean',
        'plane_found': 'boolean',
        'foreground_height_valid': 'boolean',
        'foreground_mask_available': 'boolean',
        'accepted': 'boolean',
        'reject_stage': 'string',
        'reject_reason': 'string',
        'objectness_score': 'float',
        'target_hint_score': 'float',
        'filter_score': 'float',
        'depth_score': 'float',
        'quality_score': 'float',
        'color_score': 'float',
        'shape_score': 'float',
        'physical_size_score': 'float',
        'sharpness': 'float',
        'mean_brightness': 'float',
        'dark_ratio': 'float',
        'bright_clip_ratio': 'float',
        'edge_density': 'float',
        'mask_fill_ratio': 'float',
        'mask_solidity': 'float',
        'color_similarity': 'float',
        'aspect_ratio': 'float',
        'estimated_width_m': 'float',
        'estimated_height_m': 'float',
        'sync_offset_abs_sec': 'float',
        'candidate': 'macrobot_interfaces/DepthCandidate',
        'crop_roi': 'sensor_msgs/RegionOfInterest',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
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
        rosidl_parser.definition.NamespacedType(['macrobot_interfaces', 'msg'], 'DepthCandidate'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['sensor_msgs', 'msg'], 'RegionOfInterest'),  # noqa: E501
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
        from std_msgs.msg import Header
        self.image_header = kwargs.get('image_header', Header())
        self.candidate_id = kwargs.get('candidate_id', int())
        self.crop_index = kwargs.get('crop_index', int())
        self.frame_crop_count = kwargs.get('frame_crop_count', int())
        self.target_object = kwargs.get('target_object', str())
        self.reference_profile_available = kwargs.get('reference_profile_available', bool())
        self.reference_image_count = kwargs.get('reference_image_count', int())
        self.camera_info_available = kwargs.get('camera_info_available', bool())
        self.plane_found = kwargs.get('plane_found', bool())
        self.foreground_height_valid = kwargs.get('foreground_height_valid', bool())
        self.foreground_mask_available = kwargs.get('foreground_mask_available', bool())
        self.accepted = kwargs.get('accepted', bool())
        self.reject_stage = kwargs.get('reject_stage', str())
        self.reject_reason = kwargs.get('reject_reason', str())
        self.objectness_score = kwargs.get('objectness_score', float())
        self.target_hint_score = kwargs.get('target_hint_score', float())
        self.filter_score = kwargs.get('filter_score', float())
        self.depth_score = kwargs.get('depth_score', float())
        self.quality_score = kwargs.get('quality_score', float())
        self.color_score = kwargs.get('color_score', float())
        self.shape_score = kwargs.get('shape_score', float())
        self.physical_size_score = kwargs.get('physical_size_score', float())
        self.sharpness = kwargs.get('sharpness', float())
        self.mean_brightness = kwargs.get('mean_brightness', float())
        self.dark_ratio = kwargs.get('dark_ratio', float())
        self.bright_clip_ratio = kwargs.get('bright_clip_ratio', float())
        self.edge_density = kwargs.get('edge_density', float())
        self.mask_fill_ratio = kwargs.get('mask_fill_ratio', float())
        self.mask_solidity = kwargs.get('mask_solidity', float())
        self.color_similarity = kwargs.get('color_similarity', float())
        self.aspect_ratio = kwargs.get('aspect_ratio', float())
        self.estimated_width_m = kwargs.get('estimated_width_m', float())
        self.estimated_height_m = kwargs.get('estimated_height_m', float())
        self.sync_offset_abs_sec = kwargs.get('sync_offset_abs_sec', float())
        from macrobot_interfaces.msg import DepthCandidate
        self.candidate = kwargs.get('candidate', DepthCandidate())
        from sensor_msgs.msg import RegionOfInterest
        self.crop_roi = kwargs.get('crop_roi', RegionOfInterest())

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
        if self.image_header != other.image_header:
            return False
        if self.candidate_id != other.candidate_id:
            return False
        if self.crop_index != other.crop_index:
            return False
        if self.frame_crop_count != other.frame_crop_count:
            return False
        if self.target_object != other.target_object:
            return False
        if self.reference_profile_available != other.reference_profile_available:
            return False
        if self.reference_image_count != other.reference_image_count:
            return False
        if self.camera_info_available != other.camera_info_available:
            return False
        if self.plane_found != other.plane_found:
            return False
        if self.foreground_height_valid != other.foreground_height_valid:
            return False
        if self.foreground_mask_available != other.foreground_mask_available:
            return False
        if self.accepted != other.accepted:
            return False
        if self.reject_stage != other.reject_stage:
            return False
        if self.reject_reason != other.reject_reason:
            return False
        if self.objectness_score != other.objectness_score:
            return False
        if self.target_hint_score != other.target_hint_score:
            return False
        if self.filter_score != other.filter_score:
            return False
        if self.depth_score != other.depth_score:
            return False
        if self.quality_score != other.quality_score:
            return False
        if self.color_score != other.color_score:
            return False
        if self.shape_score != other.shape_score:
            return False
        if self.physical_size_score != other.physical_size_score:
            return False
        if self.sharpness != other.sharpness:
            return False
        if self.mean_brightness != other.mean_brightness:
            return False
        if self.dark_ratio != other.dark_ratio:
            return False
        if self.bright_clip_ratio != other.bright_clip_ratio:
            return False
        if self.edge_density != other.edge_density:
            return False
        if self.mask_fill_ratio != other.mask_fill_ratio:
            return False
        if self.mask_solidity != other.mask_solidity:
            return False
        if self.color_similarity != other.color_similarity:
            return False
        if self.aspect_ratio != other.aspect_ratio:
            return False
        if self.estimated_width_m != other.estimated_width_m:
            return False
        if self.estimated_height_m != other.estimated_height_m:
            return False
        if self.sync_offset_abs_sec != other.sync_offset_abs_sec:
            return False
        if self.candidate != other.candidate:
            return False
        if self.crop_roi != other.crop_roi:
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
    def image_header(self):
        """Message field 'image_header'."""
        return self._image_header

    @image_header.setter
    def image_header(self, value):
        if self._check_fields:
            from std_msgs.msg import Header
            assert \
                isinstance(value, Header), \
                "The 'image_header' field must be a sub message of type 'Header'"
        self._image_header = value

    @builtins.property
    def candidate_id(self):
        """Message field 'candidate_id'."""
        return self._candidate_id

    @candidate_id.setter
    def candidate_id(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'candidate_id' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'candidate_id' field must be an unsigned integer in [0, 4294967295]"
        self._candidate_id = value

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
    def target_object(self):
        """Message field 'target_object'."""
        return self._target_object

    @target_object.setter
    def target_object(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'target_object' field must be of type 'str'"
        self._target_object = value

    @builtins.property
    def reference_profile_available(self):
        """Message field 'reference_profile_available'."""
        return self._reference_profile_available

    @reference_profile_available.setter
    def reference_profile_available(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'reference_profile_available' field must be of type 'bool'"
        self._reference_profile_available = value

    @builtins.property
    def reference_image_count(self):
        """Message field 'reference_image_count'."""
        return self._reference_image_count

    @reference_image_count.setter
    def reference_image_count(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'reference_image_count' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'reference_image_count' field must be an unsigned integer in [0, 4294967295]"
        self._reference_image_count = value

    @builtins.property
    def camera_info_available(self):
        """Message field 'camera_info_available'."""
        return self._camera_info_available

    @camera_info_available.setter
    def camera_info_available(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'camera_info_available' field must be of type 'bool'"
        self._camera_info_available = value

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
    def accepted(self):
        """Message field 'accepted'."""
        return self._accepted

    @accepted.setter
    def accepted(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'accepted' field must be of type 'bool'"
        self._accepted = value

    @builtins.property
    def reject_stage(self):
        """Message field 'reject_stage'."""
        return self._reject_stage

    @reject_stage.setter
    def reject_stage(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'reject_stage' field must be of type 'str'"
        self._reject_stage = value

    @builtins.property
    def reject_reason(self):
        """Message field 'reject_reason'."""
        return self._reject_reason

    @reject_reason.setter
    def reject_reason(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'reject_reason' field must be of type 'str'"
        self._reject_reason = value

    @builtins.property
    def objectness_score(self):
        """Message field 'objectness_score'."""
        return self._objectness_score

    @objectness_score.setter
    def objectness_score(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'objectness_score' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'objectness_score' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._objectness_score = value

    @builtins.property
    def target_hint_score(self):
        """Message field 'target_hint_score'."""
        return self._target_hint_score

    @target_hint_score.setter
    def target_hint_score(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'target_hint_score' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'target_hint_score' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._target_hint_score = value

    @builtins.property
    def filter_score(self):
        """Message field 'filter_score'."""
        return self._filter_score

    @filter_score.setter
    def filter_score(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'filter_score' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'filter_score' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._filter_score = value

    @builtins.property
    def depth_score(self):
        """Message field 'depth_score'."""
        return self._depth_score

    @depth_score.setter
    def depth_score(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'depth_score' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'depth_score' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._depth_score = value

    @builtins.property
    def quality_score(self):
        """Message field 'quality_score'."""
        return self._quality_score

    @quality_score.setter
    def quality_score(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'quality_score' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'quality_score' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._quality_score = value

    @builtins.property
    def color_score(self):
        """Message field 'color_score'."""
        return self._color_score

    @color_score.setter
    def color_score(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'color_score' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'color_score' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._color_score = value

    @builtins.property
    def shape_score(self):
        """Message field 'shape_score'."""
        return self._shape_score

    @shape_score.setter
    def shape_score(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'shape_score' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'shape_score' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._shape_score = value

    @builtins.property
    def physical_size_score(self):
        """Message field 'physical_size_score'."""
        return self._physical_size_score

    @physical_size_score.setter
    def physical_size_score(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'physical_size_score' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'physical_size_score' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._physical_size_score = value

    @builtins.property
    def sharpness(self):
        """Message field 'sharpness'."""
        return self._sharpness

    @sharpness.setter
    def sharpness(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'sharpness' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'sharpness' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._sharpness = value

    @builtins.property
    def mean_brightness(self):
        """Message field 'mean_brightness'."""
        return self._mean_brightness

    @mean_brightness.setter
    def mean_brightness(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'mean_brightness' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'mean_brightness' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._mean_brightness = value

    @builtins.property
    def dark_ratio(self):
        """Message field 'dark_ratio'."""
        return self._dark_ratio

    @dark_ratio.setter
    def dark_ratio(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'dark_ratio' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'dark_ratio' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._dark_ratio = value

    @builtins.property
    def bright_clip_ratio(self):
        """Message field 'bright_clip_ratio'."""
        return self._bright_clip_ratio

    @bright_clip_ratio.setter
    def bright_clip_ratio(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'bright_clip_ratio' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'bright_clip_ratio' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._bright_clip_ratio = value

    @builtins.property
    def edge_density(self):
        """Message field 'edge_density'."""
        return self._edge_density

    @edge_density.setter
    def edge_density(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'edge_density' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'edge_density' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._edge_density = value

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
    def mask_solidity(self):
        """Message field 'mask_solidity'."""
        return self._mask_solidity

    @mask_solidity.setter
    def mask_solidity(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'mask_solidity' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'mask_solidity' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._mask_solidity = value

    @builtins.property
    def color_similarity(self):
        """Message field 'color_similarity'."""
        return self._color_similarity

    @color_similarity.setter
    def color_similarity(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'color_similarity' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'color_similarity' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._color_similarity = value

    @builtins.property
    def aspect_ratio(self):
        """Message field 'aspect_ratio'."""
        return self._aspect_ratio

    @aspect_ratio.setter
    def aspect_ratio(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'aspect_ratio' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'aspect_ratio' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._aspect_ratio = value

    @builtins.property
    def estimated_width_m(self):
        """Message field 'estimated_width_m'."""
        return self._estimated_width_m

    @estimated_width_m.setter
    def estimated_width_m(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'estimated_width_m' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'estimated_width_m' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._estimated_width_m = value

    @builtins.property
    def estimated_height_m(self):
        """Message field 'estimated_height_m'."""
        return self._estimated_height_m

    @estimated_height_m.setter
    def estimated_height_m(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'estimated_height_m' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'estimated_height_m' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._estimated_height_m = value

    @builtins.property
    def sync_offset_abs_sec(self):
        """Message field 'sync_offset_abs_sec'."""
        return self._sync_offset_abs_sec

    @sync_offset_abs_sec.setter
    def sync_offset_abs_sec(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'sync_offset_abs_sec' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'sync_offset_abs_sec' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._sync_offset_abs_sec = value

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
