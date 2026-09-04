#!/usr/bin/env python3
from __future__ import annotations

import json
import math
from pathlib import Path
import struct
import sys
import xml.etree.ElementTree as ET

import yaml

REVISION = 'macrobot-serial-2axis-2026-09-04-r4'
EXPECTED_COLLISION_TRIANGLES = {'back_left_wheel_collision.stl': 590, 'back_right_wheel_collision.stl': 590, 'base_link_collision.stl': 45174, 'camera_link_collision.stl': 416, 'front_left_wheel_collision.stl': 590, 'front_right_wheel_collision.stl': 590, 'gripper_clamp_left_collision.stl': 502, 'gripper_clamp_right_collision.stl': 502, 'gripper_left_addition_collision.stl': 1240, 'gripper_left_gear_collision.stl': 5232, 'gripper_link_collision.stl': 24199, 'gripper_right_addition_collision.stl': 1240, 'gripper_right_gear_collision.stl': 5204, 'gripper_servo_gear_collision.stl': 20836, 'robot_arm_link_collision.stl': 7879}
EXPECTED_ZERO = (-0.18190005573781895, 0.06300000309218803, 0.22699793699942175)
EXPECTED_SHOULDER_AXIS_BASE = (0.0, 1.0, 0.0)
EXPECTED_WRIST_AXIS_BASE = (0.0, 1.0, 0.0)


def vec(text):
    return tuple(float(v) for v in text.split())


def close(a, b, tol=1e-6):
    return len(a) == len(b) and all(abs(x-y) <= tol for x,y in zip(a,b))


def rotation_rpy(rpy):
    r,p,y = rpy
    cr,sr=math.cos(r),math.sin(r); cp,sp=math.cos(p),math.sin(p); cy,sy=math.cos(y),math.sin(y)
    return (
        (cy*cp, cy*sp*sr-sy*cr, cy*sp*cr+sy*sr),
        (sy*cp, sy*sp*sr+cy*cr, sy*sp*cr-cy*sr),
        (-sp, cp*sr, cp*cr),
    )


def matvec(a, v):
    return tuple(sum(a[i][k]*v[k] for k in range(3)) for i in range(3))


def matmul(a, b):
    return tuple(tuple(sum(a[i][k]*b[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def add(a,b):
    return tuple(x+y for x,y in zip(a,b))


def binary_stl_triangles(path):
    data=path.read_bytes()
    if len(data)<84:
        raise ValueError('short binary STL')
    count=struct.unpack('<I',data[80:84])[0]
    if len(data)!=84+50*count:
        raise ValueError('non-canonical binary STL size')
    return count


def main():
    package=Path(sys.argv[1]).resolve() if len(sys.argv)>1 else Path(__file__).resolve().parents[1]
    errors=[]; warnings=[]
    urdf=package/'urdf/macrobot.urdf'
    root=ET.parse(urdf).getroot()
    links=[e.attrib['name'] for e in root.findall('link')]
    joints=[e.attrib['name'] for e in root.findall('joint')]
    jm={e.attrib['name']:e for e in root.findall('joint')}
    children=[e.find('child').attrib['link'] for e in root.findall('joint')]
    roots=sorted(set(links)-set(children))
    if len(links)!=18: errors.append(f'expected 18 links, got {len(links)}')
    if len(joints)!=17: errors.append(f'expected 17 joints, got {len(joints)}')
    if roots!=['base_link']: errors.append(f'unexpected roots: {roots}')
    if len(set(links))!=len(links): errors.append('duplicate links')
    if len(set(joints))!=len(joints): errors.append('duplicate joints')

    required_types={
        'arm_lift_joint':'revolute','wrist_pitch_joint':'revolute','gripper_joint':'revolute',
        'camera_fix_joint':'fixed','tool0_fixed_joint':'fixed','grasp_nominal_fixed_joint':'fixed',
    }
    for name,typ in required_types.items():
        if name not in jm: errors.append(f'missing joint: {name}')
        elif jm[name].attrib.get('type')!=typ: errors.append(f'{name} type is not {typ}')

    def origin_axis(name):
        j=jm[name]; o=j.find('origin'); a=j.find('axis')
        return vec(o.attrib['xyz']),vec(o.attrib['rpy']),vec(a.attrib['xyz']) if a is not None else None

    cxyz,crpy,_=origin_axis('camera_fix_joint')
    if not close(cxyz,(-0.030650,0.060623,0.025820)): errors.append(f'camera anchor changed: {cxyz}')
    if not close(crpy,(0.0,0.0,0.0)): errors.append(f'camera anchor rotation changed: {crpy}')

    sxyz,srpy,saxis=origin_axis('arm_lift_joint')
    wxyz,wrpy,waxis=origin_axis('wrist_pitch_joint')
    if not close(sxyz,(0.03,0.0937,0.0579)): errors.append(f'shoulder xyz mismatch: {sxyz}')
    if not close(wxyz,(0.161,0.0004,0.01)): errors.append(f'wrist xyz mismatch: {wxyz}')
    rs=rotation_rpy(srpy); rw=rotation_rpy(wrpy)
    sbase=matvec(rs,saxis); wbase=matvec(matmul(rs,rw),waxis)
    if not close(sbase,EXPECTED_SHOULDER_AXIS_BASE,1e-5): errors.append(f'shoulder axis not base +Y: {sbase}')
    if not close(wbase,EXPECTED_WRIST_AXIS_BASE,1e-5): errors.append(f'wrist axis not base +Y: {wbase}')
    dot=sum(a*b for a,b in zip(sbase,wbase))
    if dot<0.99999: errors.append(f'arm axes not parallel/aligned: dot={dot}')

    expected_mimics={
        'gripper_servo_joint':('gripper_joint',2.0),
        'gripper_left_gear_joint':('gripper_joint',-1.0),
        'gripper_right_gear_joint':('gripper_joint',1.0),
        'gripper_left_addition_joint':('gripper_joint',-1.0),
        'gripper_right_addition_joint':('gripper_joint',1.0),
        'clamp_left_addition_joint':('gripper_joint',1.0),
        'clamp_right_addition_joint':('gripper_joint',-1.0),
    }
    for name,(master,mult) in expected_mimics.items():
        j=jm.get(name); m=j.find('mimic') if j is not None else None
        if m is None: errors.append(f'{name} missing mimic'); continue
        if m.attrib.get('joint')!=master or abs(float(m.attrib.get('multiplier','nan'))-mult)>1e-9:
            errors.append(f'{name} mimic mismatch')

    # Verify effective servo/left-gear rotation vectors are opposite and 2:1.
    _,servo_rpy,servo_axis=origin_axis('gripper_servo_joint')
    _,left_rpy,left_axis=origin_axis('gripper_left_gear_joint')
    servo_eff=tuple(2.0*x for x in matvec(rotation_rpy(servo_rpy),servo_axis))
    left_eff=tuple(-1.0*x for x in matvec(rotation_rpy(left_rpy),left_axis))
    sn=math.sqrt(sum(x*x for x in servo_eff)); ln=math.sqrt(sum(x*x for x in left_eff))
    cosine=sum(a*b for a,b in zip(servo_eff,left_eff))/(sn*ln)
    if abs(sn/ln-2.0)>1e-6 or cosine>-0.99999:
        errors.append(f'gripper servo gear direction/ratio mismatch: servo={servo_eff}, left={left_eff}')

    go=jm['grasp_nominal_fixed_joint'].find('origin')
    gxyz=vec(go.attrib['xyz'])
    if not close(gxyz,(0.0207,0.2115,-0.008098)): errors.append(f'grasp local mismatch: {gxyz}')
    zero=add(sxyz,add(matvec(rs,wxyz),matvec(matmul(rs,rw),gxyz)))
    if not close(zero,EXPECTED_ZERO,2e-6): errors.append(f'zero grasp mismatch: {zero}')

    active_text='\n'.join((package/p).read_text(errors='replace') for p in ['urdf/macrobot.urdf','urdf/assemblies/macrobot_2axis_full.urdf.xacro'])
    for token in ['ratio_left_gear_joint','ratio_right_gear_joint','back_link_top_link_joint','<ros2_control','q1 + q2']:
        if token in active_text: errors.append(f'forbidden legacy/generated token: {token}')

    for mesh in root.findall('.//mesh'):
        uri=mesh.attrib.get('filename',''); prefix='package://macrobot_description/'
        if uri.startswith(prefix) and not (package/uri[len(prefix):]).is_file(): errors.append(f'missing mesh: {uri}')

    collision_dir=package/'meshes/macrobot'; collision_counts={}
    for name,expected in EXPECTED_COLLISION_TRIANGLES.items():
        path=collision_dir/name
        if not path.is_file(): errors.append(f'missing collision STL: {name}'); continue
        try:
            actual=binary_stl_triangles(path); collision_counts[name]=actual
            if actual!=expected: errors.append(f'{name} triangle mismatch: {actual} != {expected}')
        except Exception as exc: errors.append(f'{name}: {exc}')

    # ROS parameter arrays used as doubles must not mix YAML ints and floats.
    params=yaml.safe_load((package/'config/kinematics.yaml').read_text())['/**']['ros__parameters']
    vector_keys=['shoulder_origin_xyz','shoulder_origin_rpy','shoulder_axis','wrist_origin_xyz','wrist_origin_rpy','wrist_axis','grasp_origin_xyz','grasp_origin_rpy','nominal_grasp_xyz_in_gripper_link','nominal_grasp_rpy_in_gripper_link','shoulder_axis_base','wrist_axis_base_zero','arm_axis_base_xy','positive_tilt_direction_base_xy']
    for key in vector_keys:
        value=params.get(key)
        if not isinstance(value,list) or not all(type(x) is float for x in value):
            errors.append(f'kinematics.yaml {key} is not a homogeneous double array: {value!r}')
    if params.get('model_revision')!=REVISION: errors.append('kinematics revision mismatch')

    for rel in ['config/collision_model_revision.txt','config/arm_semantics.yaml','config/downstream_migration.yaml','config/camera_anchor_contract.yaml']:
        if REVISION not in (package/rel).read_text(errors='replace'): errors.append(f'revision missing in {rel}')

    parsed=[]
    for path in sorted(list((package/'urdf').rglob('*.xacro'))+[package/'package.xml']):
        try: ET.parse(path); parsed.append(str(path.relative_to(package)))
        except Exception as exc: errors.append(f'XML parse failed {path.relative_to(package)}: {exc}')
    compiled=[]
    for path in sorted((package/'launch').glob('*.py')):
        try: compile(path.read_text(),str(path),'exec'); compiled.append(str(path.relative_to(package)))
        except Exception as exc: errors.append(f'launch syntax failed {path.name}: {exc}')

    result={
        'model_revision':REVISION,'source_archive':'macrobot_description(4).zip','link_count':len(links),'joint_count':len(joints),'roots':roots,
        'shoulder_axis_base':list(sbase),'wrist_axis_base_zero':list(wbase),'axis_alignment':dot,
        'zero_pose_grasp_nominal_xyz_base_m':list(zero),'gripper_servo_effective_vector_per_q3':list(servo_eff),
        'collision_triangle_counts':collision_counts,'parsed_xml_files':parsed,'compiled_launch_files':compiled,
        'warnings':warnings,'errors':errors,'passed':not errors,
    }
    print(json.dumps(result,indent=2))
    return 0 if not errors else 1


if __name__=='__main__':
    raise SystemExit(main())
