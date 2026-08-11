# generated from rosidl_generator_py/resource/_idl.py.em
# with input from macrobot_interfaces:msg/TemporalConfirmationResult.idl
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


class Metaclass_TemporalConfirmationResult(type):
    """Metaclass of message 'TemporalConfirmationResult'."""

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
                'macrobot_interfaces.msg.TemporalConfirmationResult')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__temporal_confirmation_result
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__temporal_confirmation_result
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__temporal_confirmation_result
            cls._TYPE_SUPPORT = module.type_support_msg__msg__temporal_confirmation_result
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__temporal_confirmation_result

            from macrobot_interfaces.msg import EmbeddingRetrievalResult
            if EmbeddingRetrievalResult.__class__._TYPE_SUPPORT is None:
                EmbeddingRetrievalResult.__class__.__import_type_support__()

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


class TemporalConfirmationResult(metaclass=Metaclass_TemporalConfirmationResult):
    """Message class 'TemporalConfirmationResult'."""

    __slots__ = [
        '_header',
        '_target_object',
        '_track_id',
        '_frame_index',
        '_state',
        '_event',
        '_confirmed',
        '_track_age_frames',
        '_window_size',
        '_required_hits',
        '_samples_in_window',
        '_matched_frames_in_window',
        '_hits_in_window',
        '_misses_in_window',
        '_consecutive_hits',
        '_consecutive_misses',
        '_hit_ratio',
        '_temporal_score',
        '_stability_score',
        '_mean_positive_similarity',
        '_mean_negative_similarity',
        '_mean_margin',
        '_min_margin_in_window',
        '_mean_objectness_score',
        '_roi',
        '_center_x',
        '_center_y',
        '_depth_m',
        '_center_std_px',
        '_depth_std_m',
        '_horizontal_error_norm',
        '_suggested_turn',
        '_latest_result',
        '_check_fields',
    ]

    _fields_and_field_types = {
        'header': 'std_msgs/Header',
        'target_object': 'string',
        'track_id': 'uint32',
        'frame_index': 'uint64',
        'state': 'string',
        'event': 'string',
        'confirmed': 'boolean',
        'track_age_frames': 'uint32',
        'window_size': 'uint32',
        'required_hits': 'uint32',
        'samples_in_window': 'uint32',
        'matched_frames_in_window': 'uint32',
        'hits_in_window': 'uint32',
        'misses_in_window': 'uint32',
        'consecutive_hits': 'uint32',
        'consecutive_misses': 'uint32',
        'hit_ratio': 'float',
        'temporal_score': 'float',
        'stability_score': 'float',
        'mean_positive_similarity': 'float',
        'mean_negative_similarity': 'float',
        'mean_margin': 'float',
        'min_margin_in_window': 'float',
        'mean_objectness_score': 'float',
        'roi': 'sensor_msgs/RegionOfInterest',
        'center_x': 'float',
        'center_y': 'float',
        'depth_m': 'float',
        'center_std_px': 'float',
        'depth_std_m': 'float',
        'horizontal_error_norm': 'float',
        'suggested_turn': 'string',
        'latest_result': 'macrobot_interfaces/EmbeddingRetrievalResult',
    }

    # This attribute is used to store an rosidl_parser.definition variable
    # related to the data type of each of the components the message.
    SLOT_TYPES = (
        rosidl_parser.definition.NamespacedType(['std_msgs', 'msg'], 'Header'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint64'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['sensor_msgs', 'msg'], 'RegionOfInterest'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.NamespacedType(['macrobot_interfaces', 'msg'], 'EmbeddingRetrievalResult'),  # noqa: E501
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
        self.target_object = kwargs.get('target_object', str())
        self.track_id = kwargs.get('track_id', int())
        self.frame_index = kwargs.get('frame_index', int())
        self.state = kwargs.get('state', str())
        self.event = kwargs.get('event', str())
        self.confirmed = kwargs.get('confirmed', bool())
        self.track_age_frames = kwargs.get('track_age_frames', int())
        self.window_size = kwargs.get('window_size', int())
        self.required_hits = kwargs.get('required_hits', int())
        self.samples_in_window = kwargs.get('samples_in_window', int())
        self.matched_frames_in_window = kwargs.get('matched_frames_in_window', int())
        self.hits_in_window = kwargs.get('hits_in_window', int())
        self.misses_in_window = kwargs.get('misses_in_window', int())
        self.consecutive_hits = kwargs.get('consecutive_hits', int())
        self.consecutive_misses = kwargs.get('consecutive_misses', int())
        self.hit_ratio = kwargs.get('hit_ratio', float())
        self.temporal_score = kwargs.get('temporal_score', float())
        self.stability_score = kwargs.get('stability_score', float())
        self.mean_positive_similarity = kwargs.get('mean_positive_similarity', float())
        self.mean_negative_similarity = kwargs.get('mean_negative_similarity', float())
        self.mean_margin = kwargs.get('mean_margin', float())
        self.min_margin_in_window = kwargs.get('min_margin_in_window', float())
        self.mean_objectness_score = kwargs.get('mean_objectness_score', float())
        from sensor_msgs.msg import RegionOfInterest
        self.roi = kwargs.get('roi', RegionOfInterest())
        self.center_x = kwargs.get('center_x', float())
        self.center_y = kwargs.get('center_y', float())
        self.depth_m = kwargs.get('depth_m', float())
        self.center_std_px = kwargs.get('center_std_px', float())
        self.depth_std_m = kwargs.get('depth_std_m', float())
        self.horizontal_error_norm = kwargs.get('horizontal_error_norm', float())
        self.suggested_turn = kwargs.get('suggested_turn', str())
        from macrobot_interfaces.msg import EmbeddingRetrievalResult
        self.latest_result = kwargs.get('latest_result', EmbeddingRetrievalResult())

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
        if self.target_object != other.target_object:
            return False
        if self.track_id != other.track_id:
            return False
        if self.frame_index != other.frame_index:
            return False
        if self.state != other.state:
            return False
        if self.event != other.event:
            return False
        if self.confirmed != other.confirmed:
            return False
        if self.track_age_frames != other.track_age_frames:
            return False
        if self.window_size != other.window_size:
            return False
        if self.required_hits != other.required_hits:
            return False
        if self.samples_in_window != other.samples_in_window:
            return False
        if self.matched_frames_in_window != other.matched_frames_in_window:
            return False
        if self.hits_in_window != other.hits_in_window:
            return False
        if self.misses_in_window != other.misses_in_window:
            return False
        if self.consecutive_hits != other.consecutive_hits:
            return False
        if self.consecutive_misses != other.consecutive_misses:
            return False
        if self.hit_ratio != other.hit_ratio:
            return False
        if self.temporal_score != other.temporal_score:
            return False
        if self.stability_score != other.stability_score:
            return False
        if self.mean_positive_similarity != other.mean_positive_similarity:
            return False
        if self.mean_negative_similarity != other.mean_negative_similarity:
            return False
        if self.mean_margin != other.mean_margin:
            return False
        if self.min_margin_in_window != other.min_margin_in_window:
            return False
        if self.mean_objectness_score != other.mean_objectness_score:
            return False
        if self.roi != other.roi:
            return False
        if self.center_x != other.center_x:
            return False
        if self.center_y != other.center_y:
            return False
        if self.depth_m != other.depth_m:
            return False
        if self.center_std_px != other.center_std_px:
            return False
        if self.depth_std_m != other.depth_std_m:
            return False
        if self.horizontal_error_norm != other.horizontal_error_norm:
            return False
        if self.suggested_turn != other.suggested_turn:
            return False
        if self.latest_result != other.latest_result:
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
    def track_id(self):
        """Message field 'track_id'."""
        return self._track_id

    @track_id.setter
    def track_id(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'track_id' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'track_id' field must be an unsigned integer in [0, 4294967295]"
        self._track_id = value

    @builtins.property
    def frame_index(self):
        """Message field 'frame_index'."""
        return self._frame_index

    @frame_index.setter
    def frame_index(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'frame_index' field must be of type 'int'"
            assert value >= 0 and value < 18446744073709551616, \
                "The 'frame_index' field must be an unsigned integer in [0, 18446744073709551615]"
        self._frame_index = value

    @builtins.property
    def state(self):
        """Message field 'state'."""
        return self._state

    @state.setter
    def state(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'state' field must be of type 'str'"
        self._state = value

    @builtins.property
    def event(self):
        """Message field 'event'."""
        return self._event

    @event.setter
    def event(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'event' field must be of type 'str'"
        self._event = value

    @builtins.property
    def confirmed(self):
        """Message field 'confirmed'."""
        return self._confirmed

    @confirmed.setter
    def confirmed(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'confirmed' field must be of type 'bool'"
        self._confirmed = value

    @builtins.property
    def track_age_frames(self):
        """Message field 'track_age_frames'."""
        return self._track_age_frames

    @track_age_frames.setter
    def track_age_frames(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'track_age_frames' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'track_age_frames' field must be an unsigned integer in [0, 4294967295]"
        self._track_age_frames = value

    @builtins.property
    def window_size(self):
        """Message field 'window_size'."""
        return self._window_size

    @window_size.setter
    def window_size(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'window_size' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'window_size' field must be an unsigned integer in [0, 4294967295]"
        self._window_size = value

    @builtins.property
    def required_hits(self):
        """Message field 'required_hits'."""
        return self._required_hits

    @required_hits.setter
    def required_hits(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'required_hits' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'required_hits' field must be an unsigned integer in [0, 4294967295]"
        self._required_hits = value

    @builtins.property
    def samples_in_window(self):
        """Message field 'samples_in_window'."""
        return self._samples_in_window

    @samples_in_window.setter
    def samples_in_window(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'samples_in_window' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'samples_in_window' field must be an unsigned integer in [0, 4294967295]"
        self._samples_in_window = value

    @builtins.property
    def matched_frames_in_window(self):
        """Message field 'matched_frames_in_window'."""
        return self._matched_frames_in_window

    @matched_frames_in_window.setter
    def matched_frames_in_window(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'matched_frames_in_window' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'matched_frames_in_window' field must be an unsigned integer in [0, 4294967295]"
        self._matched_frames_in_window = value

    @builtins.property
    def hits_in_window(self):
        """Message field 'hits_in_window'."""
        return self._hits_in_window

    @hits_in_window.setter
    def hits_in_window(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'hits_in_window' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'hits_in_window' field must be an unsigned integer in [0, 4294967295]"
        self._hits_in_window = value

    @builtins.property
    def misses_in_window(self):
        """Message field 'misses_in_window'."""
        return self._misses_in_window

    @misses_in_window.setter
    def misses_in_window(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'misses_in_window' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'misses_in_window' field must be an unsigned integer in [0, 4294967295]"
        self._misses_in_window = value

    @builtins.property
    def consecutive_hits(self):
        """Message field 'consecutive_hits'."""
        return self._consecutive_hits

    @consecutive_hits.setter
    def consecutive_hits(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'consecutive_hits' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'consecutive_hits' field must be an unsigned integer in [0, 4294967295]"
        self._consecutive_hits = value

    @builtins.property
    def consecutive_misses(self):
        """Message field 'consecutive_misses'."""
        return self._consecutive_misses

    @consecutive_misses.setter
    def consecutive_misses(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'consecutive_misses' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'consecutive_misses' field must be an unsigned integer in [0, 4294967295]"
        self._consecutive_misses = value

    @builtins.property
    def hit_ratio(self):
        """Message field 'hit_ratio'."""
        return self._hit_ratio

    @hit_ratio.setter
    def hit_ratio(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'hit_ratio' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'hit_ratio' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._hit_ratio = value

    @builtins.property
    def temporal_score(self):
        """Message field 'temporal_score'."""
        return self._temporal_score

    @temporal_score.setter
    def temporal_score(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'temporal_score' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'temporal_score' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._temporal_score = value

    @builtins.property
    def stability_score(self):
        """Message field 'stability_score'."""
        return self._stability_score

    @stability_score.setter
    def stability_score(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'stability_score' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'stability_score' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._stability_score = value

    @builtins.property
    def mean_positive_similarity(self):
        """Message field 'mean_positive_similarity'."""
        return self._mean_positive_similarity

    @mean_positive_similarity.setter
    def mean_positive_similarity(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'mean_positive_similarity' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'mean_positive_similarity' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._mean_positive_similarity = value

    @builtins.property
    def mean_negative_similarity(self):
        """Message field 'mean_negative_similarity'."""
        return self._mean_negative_similarity

    @mean_negative_similarity.setter
    def mean_negative_similarity(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'mean_negative_similarity' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'mean_negative_similarity' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._mean_negative_similarity = value

    @builtins.property
    def mean_margin(self):
        """Message field 'mean_margin'."""
        return self._mean_margin

    @mean_margin.setter
    def mean_margin(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'mean_margin' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'mean_margin' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._mean_margin = value

    @builtins.property
    def min_margin_in_window(self):
        """Message field 'min_margin_in_window'."""
        return self._min_margin_in_window

    @min_margin_in_window.setter
    def min_margin_in_window(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'min_margin_in_window' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'min_margin_in_window' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._min_margin_in_window = value

    @builtins.property
    def mean_objectness_score(self):
        """Message field 'mean_objectness_score'."""
        return self._mean_objectness_score

    @mean_objectness_score.setter
    def mean_objectness_score(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'mean_objectness_score' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'mean_objectness_score' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._mean_objectness_score = value

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
    def depth_m(self):
        """Message field 'depth_m'."""
        return self._depth_m

    @depth_m.setter
    def depth_m(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'depth_m' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'depth_m' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._depth_m = value

    @builtins.property
    def center_std_px(self):
        """Message field 'center_std_px'."""
        return self._center_std_px

    @center_std_px.setter
    def center_std_px(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'center_std_px' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'center_std_px' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._center_std_px = value

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
    def horizontal_error_norm(self):
        """Message field 'horizontal_error_norm'."""
        return self._horizontal_error_norm

    @horizontal_error_norm.setter
    def horizontal_error_norm(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'horizontal_error_norm' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'horizontal_error_norm' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._horizontal_error_norm = value

    @builtins.property
    def suggested_turn(self):
        """Message field 'suggested_turn'."""
        return self._suggested_turn

    @suggested_turn.setter
    def suggested_turn(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'suggested_turn' field must be of type 'str'"
        self._suggested_turn = value

    @builtins.property
    def latest_result(self):
        """Message field 'latest_result'."""
        return self._latest_result

    @latest_result.setter
    def latest_result(self, value):
        if self._check_fields:
            from macrobot_interfaces.msg import EmbeddingRetrievalResult
            assert \
                isinstance(value, EmbeddingRetrievalResult), \
                "The 'latest_result' field must be a sub message of type 'EmbeddingRetrievalResult'"
        self._latest_result = value
