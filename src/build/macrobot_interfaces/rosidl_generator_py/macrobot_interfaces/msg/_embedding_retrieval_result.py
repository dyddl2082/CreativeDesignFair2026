# generated from rosidl_generator_py/resource/_idl.py.em
# with input from macrobot_interfaces:msg/EmbeddingRetrievalResult.idl
# generated code does not contain a copyright notice

# This is being done at the module level and not on the instance level to avoid looking
# for the same variable multiple times on each instance. This variable is not supposed to
# change during runtime so it makes sense to only look for it once.
from os import getenv

ros_python_check_fields = getenv('ROS_PYTHON_CHECK_FIELDS', default='')


# Import statements for member types

# Member 'top_positive_scores'
# Member 'top_negative_scores'
import array  # noqa: E402, I100

import builtins  # noqa: E402, I100

import math  # noqa: E402, I100

import rosidl_parser.definition  # noqa: E402, I100


class Metaclass_EmbeddingRetrievalResult(type):
    """Metaclass of message 'EmbeddingRetrievalResult'."""

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
                'macrobot_interfaces.msg.EmbeddingRetrievalResult')
            logger.debug(
                'Failed to import needed modules for type support:\n' +
                traceback.format_exc())
        else:
            cls._CREATE_ROS_MESSAGE = module.create_ros_message_msg__msg__embedding_retrieval_result
            cls._CONVERT_FROM_PY = module.convert_from_py_msg__msg__embedding_retrieval_result
            cls._CONVERT_TO_PY = module.convert_to_py_msg__msg__embedding_retrieval_result
            cls._TYPE_SUPPORT = module.type_support_msg__msg__embedding_retrieval_result
            cls._DESTROY_ROS_MESSAGE = module.destroy_ros_message_msg__msg__embedding_retrieval_result

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


class EmbeddingRetrievalResult(metaclass=Metaclass_EmbeddingRetrievalResult):
    """Message class 'EmbeddingRetrievalResult'."""

    __slots__ = [
        '_proposal_header',
        '_image_header',
        '_candidate_id',
        '_crop_index',
        '_frame_crop_count',
        '_target_object',
        '_model_id',
        '_pooling',
        '_device',
        '_embedding_dim',
        '_positive_bank_available',
        '_positive_reference_count',
        '_negative_bank_available',
        '_negative_reference_count',
        '_foreground_mask_used',
        '_objectness_score',
        '_target_hint_score',
        '_positive_similarity',
        '_best_positive_similarity',
        '_negative_similarity',
        '_best_negative_similarity',
        '_margin',
        '_best_positive_path',
        '_best_negative_path',
        '_top_positive_paths',
        '_top_positive_scores',
        '_top_negative_paths',
        '_top_negative_scores',
        '_thresholds_enforced',
        '_passed_positive_threshold',
        '_passed_margin_threshold',
        '_accepted',
        '_reject_reason',
        '_preprocessing_ms',
        '_inference_ms',
        '_matching_ms',
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
        'model_id': 'string',
        'pooling': 'string',
        'device': 'string',
        'embedding_dim': 'uint32',
        'positive_bank_available': 'boolean',
        'positive_reference_count': 'uint32',
        'negative_bank_available': 'boolean',
        'negative_reference_count': 'uint32',
        'foreground_mask_used': 'boolean',
        'objectness_score': 'float',
        'target_hint_score': 'float',
        'positive_similarity': 'float',
        'best_positive_similarity': 'float',
        'negative_similarity': 'float',
        'best_negative_similarity': 'float',
        'margin': 'float',
        'best_positive_path': 'string',
        'best_negative_path': 'string',
        'top_positive_paths': 'sequence<string>',
        'top_positive_scores': 'sequence<float>',
        'top_negative_paths': 'sequence<string>',
        'top_negative_scores': 'sequence<float>',
        'thresholds_enforced': 'boolean',
        'passed_positive_threshold': 'boolean',
        'passed_margin_threshold': 'boolean',
        'accepted': 'boolean',
        'reject_reason': 'string',
        'preprocessing_ms': 'float',
        'inference_ms': 'float',
        'matching_ms': 'float',
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
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('uint32'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.BasicType('float'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.UnboundedString()),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('float')),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.UnboundedString()),  # noqa: E501
        rosidl_parser.definition.UnboundedSequence(rosidl_parser.definition.BasicType('float')),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.BasicType('boolean'),  # noqa: E501
        rosidl_parser.definition.UnboundedString(),  # noqa: E501
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
        self.model_id = kwargs.get('model_id', str())
        self.pooling = kwargs.get('pooling', str())
        self.device = kwargs.get('device', str())
        self.embedding_dim = kwargs.get('embedding_dim', int())
        self.positive_bank_available = kwargs.get('positive_bank_available', bool())
        self.positive_reference_count = kwargs.get('positive_reference_count', int())
        self.negative_bank_available = kwargs.get('negative_bank_available', bool())
        self.negative_reference_count = kwargs.get('negative_reference_count', int())
        self.foreground_mask_used = kwargs.get('foreground_mask_used', bool())
        self.objectness_score = kwargs.get('objectness_score', float())
        self.target_hint_score = kwargs.get('target_hint_score', float())
        self.positive_similarity = kwargs.get('positive_similarity', float())
        self.best_positive_similarity = kwargs.get('best_positive_similarity', float())
        self.negative_similarity = kwargs.get('negative_similarity', float())
        self.best_negative_similarity = kwargs.get('best_negative_similarity', float())
        self.margin = kwargs.get('margin', float())
        self.best_positive_path = kwargs.get('best_positive_path', str())
        self.best_negative_path = kwargs.get('best_negative_path', str())
        self.top_positive_paths = kwargs.get('top_positive_paths', [])
        self.top_positive_scores = array.array('f', kwargs.get('top_positive_scores', []))
        self.top_negative_paths = kwargs.get('top_negative_paths', [])
        self.top_negative_scores = array.array('f', kwargs.get('top_negative_scores', []))
        self.thresholds_enforced = kwargs.get('thresholds_enforced', bool())
        self.passed_positive_threshold = kwargs.get('passed_positive_threshold', bool())
        self.passed_margin_threshold = kwargs.get('passed_margin_threshold', bool())
        self.accepted = kwargs.get('accepted', bool())
        self.reject_reason = kwargs.get('reject_reason', str())
        self.preprocessing_ms = kwargs.get('preprocessing_ms', float())
        self.inference_ms = kwargs.get('inference_ms', float())
        self.matching_ms = kwargs.get('matching_ms', float())
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
        if self.model_id != other.model_id:
            return False
        if self.pooling != other.pooling:
            return False
        if self.device != other.device:
            return False
        if self.embedding_dim != other.embedding_dim:
            return False
        if self.positive_bank_available != other.positive_bank_available:
            return False
        if self.positive_reference_count != other.positive_reference_count:
            return False
        if self.negative_bank_available != other.negative_bank_available:
            return False
        if self.negative_reference_count != other.negative_reference_count:
            return False
        if self.foreground_mask_used != other.foreground_mask_used:
            return False
        if self.objectness_score != other.objectness_score:
            return False
        if self.target_hint_score != other.target_hint_score:
            return False
        if self.positive_similarity != other.positive_similarity:
            return False
        if self.best_positive_similarity != other.best_positive_similarity:
            return False
        if self.negative_similarity != other.negative_similarity:
            return False
        if self.best_negative_similarity != other.best_negative_similarity:
            return False
        if self.margin != other.margin:
            return False
        if self.best_positive_path != other.best_positive_path:
            return False
        if self.best_negative_path != other.best_negative_path:
            return False
        if self.top_positive_paths != other.top_positive_paths:
            return False
        if self.top_positive_scores != other.top_positive_scores:
            return False
        if self.top_negative_paths != other.top_negative_paths:
            return False
        if self.top_negative_scores != other.top_negative_scores:
            return False
        if self.thresholds_enforced != other.thresholds_enforced:
            return False
        if self.passed_positive_threshold != other.passed_positive_threshold:
            return False
        if self.passed_margin_threshold != other.passed_margin_threshold:
            return False
        if self.accepted != other.accepted:
            return False
        if self.reject_reason != other.reject_reason:
            return False
        if self.preprocessing_ms != other.preprocessing_ms:
            return False
        if self.inference_ms != other.inference_ms:
            return False
        if self.matching_ms != other.matching_ms:
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
    def model_id(self):
        """Message field 'model_id'."""
        return self._model_id

    @model_id.setter
    def model_id(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'model_id' field must be of type 'str'"
        self._model_id = value

    @builtins.property
    def pooling(self):
        """Message field 'pooling'."""
        return self._pooling

    @pooling.setter
    def pooling(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'pooling' field must be of type 'str'"
        self._pooling = value

    @builtins.property
    def device(self):
        """Message field 'device'."""
        return self._device

    @device.setter
    def device(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'device' field must be of type 'str'"
        self._device = value

    @builtins.property
    def embedding_dim(self):
        """Message field 'embedding_dim'."""
        return self._embedding_dim

    @embedding_dim.setter
    def embedding_dim(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'embedding_dim' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'embedding_dim' field must be an unsigned integer in [0, 4294967295]"
        self._embedding_dim = value

    @builtins.property
    def positive_bank_available(self):
        """Message field 'positive_bank_available'."""
        return self._positive_bank_available

    @positive_bank_available.setter
    def positive_bank_available(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'positive_bank_available' field must be of type 'bool'"
        self._positive_bank_available = value

    @builtins.property
    def positive_reference_count(self):
        """Message field 'positive_reference_count'."""
        return self._positive_reference_count

    @positive_reference_count.setter
    def positive_reference_count(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'positive_reference_count' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'positive_reference_count' field must be an unsigned integer in [0, 4294967295]"
        self._positive_reference_count = value

    @builtins.property
    def negative_bank_available(self):
        """Message field 'negative_bank_available'."""
        return self._negative_bank_available

    @negative_bank_available.setter
    def negative_bank_available(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'negative_bank_available' field must be of type 'bool'"
        self._negative_bank_available = value

    @builtins.property
    def negative_reference_count(self):
        """Message field 'negative_reference_count'."""
        return self._negative_reference_count

    @negative_reference_count.setter
    def negative_reference_count(self, value):
        if self._check_fields:
            assert \
                isinstance(value, int), \
                "The 'negative_reference_count' field must be of type 'int'"
            assert value >= 0 and value < 4294967296, \
                "The 'negative_reference_count' field must be an unsigned integer in [0, 4294967295]"
        self._negative_reference_count = value

    @builtins.property
    def foreground_mask_used(self):
        """Message field 'foreground_mask_used'."""
        return self._foreground_mask_used

    @foreground_mask_used.setter
    def foreground_mask_used(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'foreground_mask_used' field must be of type 'bool'"
        self._foreground_mask_used = value

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
    def positive_similarity(self):
        """Message field 'positive_similarity'."""
        return self._positive_similarity

    @positive_similarity.setter
    def positive_similarity(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'positive_similarity' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'positive_similarity' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._positive_similarity = value

    @builtins.property
    def best_positive_similarity(self):
        """Message field 'best_positive_similarity'."""
        return self._best_positive_similarity

    @best_positive_similarity.setter
    def best_positive_similarity(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'best_positive_similarity' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'best_positive_similarity' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._best_positive_similarity = value

    @builtins.property
    def negative_similarity(self):
        """Message field 'negative_similarity'."""
        return self._negative_similarity

    @negative_similarity.setter
    def negative_similarity(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'negative_similarity' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'negative_similarity' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._negative_similarity = value

    @builtins.property
    def best_negative_similarity(self):
        """Message field 'best_negative_similarity'."""
        return self._best_negative_similarity

    @best_negative_similarity.setter
    def best_negative_similarity(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'best_negative_similarity' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'best_negative_similarity' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._best_negative_similarity = value

    @builtins.property
    def margin(self):
        """Message field 'margin'."""
        return self._margin

    @margin.setter
    def margin(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'margin' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'margin' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._margin = value

    @builtins.property
    def best_positive_path(self):
        """Message field 'best_positive_path'."""
        return self._best_positive_path

    @best_positive_path.setter
    def best_positive_path(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'best_positive_path' field must be of type 'str'"
        self._best_positive_path = value

    @builtins.property
    def best_negative_path(self):
        """Message field 'best_negative_path'."""
        return self._best_negative_path

    @best_negative_path.setter
    def best_negative_path(self, value):
        if self._check_fields:
            assert \
                isinstance(value, str), \
                "The 'best_negative_path' field must be of type 'str'"
        self._best_negative_path = value

    @builtins.property
    def top_positive_paths(self):
        """Message field 'top_positive_paths'."""
        return self._top_positive_paths

    @top_positive_paths.setter
    def top_positive_paths(self, value):
        if self._check_fields:
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
                 all(isinstance(v, str) for v in value) and
                 True), \
                "The 'top_positive_paths' field must be a set or sequence and each value of type 'str'"
        self._top_positive_paths = value

    @builtins.property
    def top_positive_scores(self):
        """Message field 'top_positive_scores'."""
        return self._top_positive_scores

    @top_positive_scores.setter
    def top_positive_scores(self, value):
        if self._check_fields:
            if isinstance(value, array.array):
                assert value.typecode == 'f', \
                    "The 'top_positive_scores' array.array() must have the type code of 'f'"
                self._top_positive_scores = value
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
                 all(isinstance(v, float) for v in value) and
                 all(not (val < -3.402823466e+38 or val > 3.402823466e+38) or math.isinf(val) for val in value)), \
                "The 'top_positive_scores' field must be a set or sequence and each value of type 'float' and each float in [-340282346600000016151267322115014000640.000000, 340282346600000016151267322115014000640.000000]"
        self._top_positive_scores = array.array('f', value)

    @builtins.property
    def top_negative_paths(self):
        """Message field 'top_negative_paths'."""
        return self._top_negative_paths

    @top_negative_paths.setter
    def top_negative_paths(self, value):
        if self._check_fields:
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
                 all(isinstance(v, str) for v in value) and
                 True), \
                "The 'top_negative_paths' field must be a set or sequence and each value of type 'str'"
        self._top_negative_paths = value

    @builtins.property
    def top_negative_scores(self):
        """Message field 'top_negative_scores'."""
        return self._top_negative_scores

    @top_negative_scores.setter
    def top_negative_scores(self, value):
        if self._check_fields:
            if isinstance(value, array.array):
                assert value.typecode == 'f', \
                    "The 'top_negative_scores' array.array() must have the type code of 'f'"
                self._top_negative_scores = value
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
                 all(isinstance(v, float) for v in value) and
                 all(not (val < -3.402823466e+38 or val > 3.402823466e+38) or math.isinf(val) for val in value)), \
                "The 'top_negative_scores' field must be a set or sequence and each value of type 'float' and each float in [-340282346600000016151267322115014000640.000000, 340282346600000016151267322115014000640.000000]"
        self._top_negative_scores = array.array('f', value)

    @builtins.property
    def thresholds_enforced(self):
        """Message field 'thresholds_enforced'."""
        return self._thresholds_enforced

    @thresholds_enforced.setter
    def thresholds_enforced(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'thresholds_enforced' field must be of type 'bool'"
        self._thresholds_enforced = value

    @builtins.property
    def passed_positive_threshold(self):
        """Message field 'passed_positive_threshold'."""
        return self._passed_positive_threshold

    @passed_positive_threshold.setter
    def passed_positive_threshold(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'passed_positive_threshold' field must be of type 'bool'"
        self._passed_positive_threshold = value

    @builtins.property
    def passed_margin_threshold(self):
        """Message field 'passed_margin_threshold'."""
        return self._passed_margin_threshold

    @passed_margin_threshold.setter
    def passed_margin_threshold(self, value):
        if self._check_fields:
            assert \
                isinstance(value, bool), \
                "The 'passed_margin_threshold' field must be of type 'bool'"
        self._passed_margin_threshold = value

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
    def preprocessing_ms(self):
        """Message field 'preprocessing_ms'."""
        return self._preprocessing_ms

    @preprocessing_ms.setter
    def preprocessing_ms(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'preprocessing_ms' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'preprocessing_ms' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._preprocessing_ms = value

    @builtins.property
    def inference_ms(self):
        """Message field 'inference_ms'."""
        return self._inference_ms

    @inference_ms.setter
    def inference_ms(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'inference_ms' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'inference_ms' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._inference_ms = value

    @builtins.property
    def matching_ms(self):
        """Message field 'matching_ms'."""
        return self._matching_ms

    @matching_ms.setter
    def matching_ms(self, value):
        if self._check_fields:
            assert \
                isinstance(value, float), \
                "The 'matching_ms' field must be of type 'float'"
            assert not (value < -3.402823466e+38 or value > 3.402823466e+38) or math.isinf(value), \
                "The 'matching_ms' field must be a float in [-3.402823466e+38, 3.402823466e+38]"
        self._matching_ms = value

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
