# MacRobot LLM Robot API Specification v0.3

## Scope

This specification synchronizes the generated-code UI contract, the Robot
Action Gateway, and the current camera-authoritative pick pipeline. The only
public objects are `ObjectId.ERASER` (`Eraser`) and `ObjectId.RUBBER`
(`Rubber`).

## Coordinate and turn convention

- Distance unit: metre.
- Angle unit: degree.
- Positive linear motion: forward.
- Positive angular motion: counterclockwise when viewed from above.
- Pico `TURN_DEG` uses the same positive-counterclockwise convention.

## High-level entry contracts

### `ALIGN_WITH_OBJECT(object_id)`

The Gateway publishes a request-ID-bearing goal to
`/macrobot/visible_pick_test/goal` with `execute_pick: false`. The goal uses the
object's canonical runtime profile and a 2400 second hard timeout. Completion
is accepted only from the matching request ID.

### `PICK_OBJECT(object_id)`

The Gateway publishes the same visible-test goal contract with
`execute_pick: true`. On success, the camera-authoritative pipeline records the
held object and semantic grasp-keyframe profile in object memory.

### `PLACE_NEXTTO_OBJECT(reference_object_id)`

Preconditions:

1. The robot is known to be holding one canonical object from the current boot
   epoch.
2. The reference object is the other canonical object; placing an object next
   to itself is rejected.
3. Runtime profiles and semantic keyframe profiles are installed:
   `Eraser`/`Eraser_r4` and `Rubber`/`Rubber_r4`.

The Gateway publishes a `task: place` goal to `/macrobot/stored_pick/goal` with
all of the following fields:

- request ID;
- reference object and reference runtime profile;
- held object and held runtime profile;
- held object's semantic grasp-keyframe profile;
- canonical adjacent offset `[0.0, 0.12, 0.0]` in `base_link`;
- `start_finder: true`, `rebuild_banks: false`, `confirm_held: false`;
- 2400 second hard timeout.

The camera-authoritative node inherits the resilient PLACE path. It searches
and aligns to the reference object, computes the target point by adding the
configured offset, validates a `preflight_place` path, and executes the
semantic reverse-grasp sequence `PLACE_ABOVE`, `PLACE_DESCEND`,
`PLACE_RELEASE`, `PLACE_RETREAT`. Successful command completion clears held
object memory and produces `stored_place_completed`.

This is not physical release verification. Until a gripper force/current or
object-presence sensor is added, success means safe preflight plus completion
of the commanded placement sequence.

## Time and motion limits

- Long visual ALIGN/PICK/PLACE hard timeout: 2400 s.
- Recommended `WAIT_ACTION` timeout for those actions: 2410 s.
- Whole generated-program wall timeout: 5000 s, allowing a sequential PICK and
  PLACE plus bounded overhead.
- Whole-program internal motion-step budget: 80.
- Base per-call limits: 1.0 m translation and 180 degrees rotation.
- Gateway base speeds: move 80, turn 150.

## Safety defaults

- UI backend `allow_execution`: false.
- Gateway `real_motion_enabled`: false.
- PLACE never sets `confirm_held: true`; unknown held state after restart
  remains a safe failure and needs explicit operator recovery.
- Generated code cannot publish ROS messages directly or calculate placement
  coordinates.
