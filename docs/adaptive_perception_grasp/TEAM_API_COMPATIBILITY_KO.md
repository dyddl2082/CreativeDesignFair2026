# 팀 LLM Robot API와의 정합성

공개 함수는 변경하지 않는다.

```text
ALIGN_WITH_OBJECT
PICK_OBJECT
GET_OBJECT_STATE
```

LLM이 threshold, pixel, TF, joint keyframe을 직접 다루지 않는다.

```text
robot.PICK_OBJECT(ObjectId.ERASER)
→ Gateway resource/timeout/cancel
→ stored-object find
→ patch-localized point
→ camera-offset-aware alignment
→ semantic keyframe IK/preflight
→ grasp
```

`PICK_OBJECT`가 내부 ALIGN을 수행하므로 생성 코드가 무조건 `ALIGN_WITH_OBJECT`를 먼저 호출하면 안 된다.
