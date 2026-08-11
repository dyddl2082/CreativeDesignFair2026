import sys
if sys.prefix == '/usr':
    sys.real_prefix = sys.prefix
    sys.prefix = sys.exec_prefix = '/home/dyddl2082/MacRobot/src/install/depth_candidate_proposal'
