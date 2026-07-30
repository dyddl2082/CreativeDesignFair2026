"use strict";

const state = {
  session: null,
  image: null,
  selection: null,
  dragging: false,
  dragStart: null,
  statsRequestSerial: 0,
  toastTimer: null,
  busy: false,
  cameraFresh: false,
  initialized: false,
  activeRole: "positive",
  roleValues: {},
  defaults: {
    positive: "Buds3",
    shared_negative: "other_object",
    background: "background",
    hard_negative: "other_object",
  },
};

const ROLE_INFO = {
  positive: {
    title: "등록 물체",
    inputLabel: "물체 이름",
    help: "목표 물체의 positive view로 저장합니다. 이 물체는 다른 모든 등록 목표를 찾을 때 자동으로 negative로 재사용됩니다.",
    saveLabel: "등록 이미지 저장",
    destination: (label) => `curated/objects/${label || "<물체>"}`,
  },
  shared_negative: {
    title: "공용 방해물",
    inputLabel: "방해물 이름",
    help: "컵·마우스·충전기처럼 목표로 등록하지 않을 물체를 한 번만 촬영합니다. 모든 목표의 negative에 자동 연결됩니다.",
    saveLabel: "공용 negative 저장",
    destination: (label) => `negative/library/${label || "<방해물>"}`,
  },
  background: {
    title: "배경·환경",
    inputLabel: "장면 이름",
    help: "빈 책상, 손, 케이블, 그림자 같은 공통 배경을 저장합니다. 모든 목표가 같은 background bank를 공유합니다.",
    saveLabel: "배경 negative 저장",
    destination: (label) => `negative/backgrounds/${label || "<장면>"}`,
  },
  hard_negative: {
    title: "목표 전용 hard negative",
    inputLabel: "혼동 물체 이름",
    help: "공용 negative와 임베딩 margin으로도 특정 목표에서 오검출이 남을 때만 사용합니다. 선택한 목표에만 적용됩니다.",
    saveLabel: "목표 전용 negative 저장",
    destination: (label, target) => `negative/confusers/${target || "<목표>"}/manual/${label || "<방해물>"}`,
  },
};

const $ = (id) => document.getElementById(id);
const els = {
  connectionBadge: $("connectionBadge"),
  syncNegativesBtn: $("syncNegativesBtn"),
  liveImage: $("liveImage"),
  livePlaceholder: $("livePlaceholder"),
  roleInputs: Array.from(document.querySelectorAll('input[name="datasetRole"]')),
  roleHelp: $("roleHelp"),
  objectNameGroup: $("objectNameGroup"),
  objectNameLabel: $("objectNameLabel"),
  objectName: $("objectName"),
  targetObjectGroup: $("targetObjectGroup"),
  targetObject: $("targetObject"),
  registeredObjects: $("registeredObjects"),
  viewLabel: $("viewLabel"),
  destinationHint: $("destinationHint"),
  captureBtn: $("captureBtn"),
  refreshStreamBtn: $("refreshStreamBtn"),
  editorPanel: $("editorPanel"),
  sessionBadge: $("sessionBadge"),
  editorCanvas: $("editorCanvas"),
  cropPreviewCanvas: $("cropPreviewCanvas"),
  cropDimensions: $("cropDimensions"),
  fullFrameBtn: $("fullFrameBtn"),
  centerSquareBtn: $("centerSquareBtn"),
  clearCropBtn: $("clearCropBtn"),
  depthMedian: $("depthMedian"),
  depthRange: $("depthRange"),
  depthValid: $("depthValid"),
  depthSync: $("depthSync"),
  saveOriginal: $("saveOriginal"),
  saveDepth: $("saveDepth"),
  notes: $("notes"),
  discardBtn: $("discardBtn"),
  saveBtn: $("saveBtn"),
  resultBox: $("resultBox"),
  toast: $("toast"),
};

function formatMeters(value) {
  return Number.isFinite(value) ? `${value.toFixed(3)} m` : "-";
}

function formatMillis(seconds) {
  return Number.isFinite(seconds) ? `${(seconds * 1000).toFixed(1)} ms` : "-";
}

function showToast(message, kind = "") {
  window.clearTimeout(state.toastTimer);
  els.toast.textContent = message;
  els.toast.className = `toast ${kind}`.trim();
  state.toastTimer = window.setTimeout(() => els.toast.classList.add("hidden"), 5200);
}

async function api(path, options = {}) {
  const response = await fetch(path, {
    method: options.method || "GET",
    headers: options.body ? { "Content-Type": "application/json" } : {},
    body: options.body ? JSON.stringify(options.body) : undefined,
    cache: "no-store",
  });
  let payload;
  try {
    payload = await response.json();
  } catch (_) {
    payload = { ok: false, error: `HTTP ${response.status}` };
  }
  if (!response.ok || payload.ok === false) {
    const details = payload.details ? ` (${payload.details})` : "";
    throw new Error(`${payload.error || `HTTP ${response.status}`}${details}`);
  }
  return payload;
}

function selectedRole() {
  return els.roleInputs.find((input) => input.checked)?.value || "positive";
}

function populateRegisteredObjects(names) {
  const unique = Array.from(new Set((names || []).filter(Boolean))).sort((a, b) => a.localeCompare(b));
  els.registeredObjects.replaceChildren(
    ...unique.map((name) => {
      const option = document.createElement("option");
      option.value = name;
      return option;
    }),
  );
}

function updateDestinationHint() {
  const role = selectedRole();
  const info = ROLE_INFO[role];
  const label = els.objectName.value.trim();
  const target = els.targetObject.value.trim();
  els.destinationHint.textContent = `저장 위치: ~/MacRobot/data/${info.destination(label, target)}`;
}

function applyRole(role, { rememberCurrent = true, setDefault = true } = {}) {
  if (!ROLE_INFO[role]) role = "positive";
  if (rememberCurrent && state.activeRole) {
    state.roleValues[state.activeRole] = els.objectName.value.trim();
  }
  state.activeRole = role;
  for (const input of els.roleInputs) input.checked = input.value === role;

  const info = ROLE_INFO[role];
  els.objectNameLabel.textContent = info.inputLabel;
  els.roleHelp.innerHTML = `<strong>${info.title}</strong><span>${info.help}</span>`;
  els.targetObjectGroup.classList.toggle("hidden", role !== "hard_negative");
  els.saveBtn.textContent = info.saveLabel;

  if (setDefault) {
    els.objectName.value = state.roleValues[role] || state.defaults[role] || "";
  }
  updateDestinationHint();
}

function validateIdentity() {
  const role = selectedRole();
  const label = els.objectName.value.trim();
  if (!label) {
    showToast(`${ROLE_INFO[role].inputLabel}을 입력하세요.`, "error");
    els.objectName.focus();
    return false;
  }
  if (role === "hard_negative" && !els.targetObject.value.trim()) {
    showToast("이 hard negative가 적용될 목표 물체를 입력하세요.", "error");
    els.targetObject.focus();
    return false;
  }
  return true;
}

async function refreshStatus() {
  try {
    const status = await api("/api/status");
    const age = status.color_age_sec;
    const fresh = status.color_available && Number.isFinite(age) && age < 2.0;
    els.connectionBadge.textContent = fresh
      ? `D435 연결됨 · Depth ${status.depth_available ? "있음" : "대기"}`
      : "D435 color 토픽 대기 중";
    els.connectionBadge.className = `badge ${fresh ? "badge-ok" : "badge-warn"}`;
    state.cameraFresh = fresh;
    els.captureBtn.disabled = state.busy || !fresh;
    els.livePlaceholder.classList.toggle("hidden", fresh && status.preview_available);
    populateRegisteredObjects(status.registered_objects);

    if (!state.initialized) {
      state.defaults.positive = status.default_object_name || "Buds3";
      state.defaults.shared_negative = status.default_shared_negative_label || "other_object";
      state.defaults.background = status.default_background_label || "background";
      state.defaults.hard_negative = status.default_shared_negative_label || "other_object";
      els.saveOriginal.checked = Boolean(status.save_original_default);
      els.saveDepth.checked = Boolean(status.save_depth_default);
      applyRole(status.default_dataset_role || "positive", {
        rememberCurrent: false,
        setDefault: true,
      });
      state.initialized = true;
    }

    if (!state.session && status.active_session) {
      await restoreSession(status.active_session);
    }
  } catch (error) {
    state.cameraFresh = false;
    els.connectionBadge.textContent = "노드 연결 실패";
    els.connectionBadge.className = "badge badge-error";
    els.captureBtn.disabled = true;
  }
}

function refreshLiveStream() {
  els.liveImage.src = `/stream.mjpg?ts=${Date.now()}`;
}

async function captureFrame() {
  if (!validateIdentity()) return;
  const role = selectedRole();
  setBusy(true, "촬영 중...", els.captureBtn);
  try {
    const payload = await api("/api/capture", {
      method: "POST",
      body: {
        dataset_role: role,
        object_name: els.objectName.value.trim(),
        target_object: els.targetObject.value.trim(),
        view_label: els.viewLabel.value.trim() || "view",
      },
    });
    await loadSession(payload);
    showToast("프레임을 고정했습니다. 저장할 영역을 조정하세요.", "success");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setBusy(false, "", els.captureBtn);
  }
}

async function restoreSession(sessionInfo) {
  const payload = {
    ...sessionInfo,
    image_url: `/api/capture.jpg?session_id=${encodeURIComponent(sessionInfo.session_id)}`,
  };
  await loadSession(payload);
}

async function loadSession(payload) {
  const image = new Image();
  image.decoding = "async";
  image.src = `${payload.image_url}&ts=${Date.now()}`;
  await image.decode();

  state.session = payload;
  state.image = image;
  state.selection = { x: 0, y: 0, width: image.naturalWidth, height: image.naturalHeight };
  applyRole(payload.dataset_role || "positive", {
    rememberCurrent: true,
    setDefault: false,
  });
  els.objectName.value = payload.object_name || els.objectName.value;
  els.targetObject.value = payload.target_object || "";
  els.viewLabel.value = payload.view_label || els.viewLabel.value;
  updateDestinationHint();
  els.editorPanel.classList.remove("hidden");
  els.sessionBadge.textContent = `${ROLE_INFO[selectedRole()].title} · ${payload.session_id.slice(0, 8)}`;
  els.depthSync.textContent = formatMillis(payload.depth_sync_offset_sec);
  resizeEditorCanvas();
  updateSelectionDisplay();
  els.editorPanel.scrollIntoView({ behavior: "smooth", block: "start" });
}

function resizeEditorCanvas() {
  if (!state.image) return;
  els.editorCanvas.width = state.image.naturalWidth;
  els.editorCanvas.height = state.image.naturalHeight;
  drawEditor();
}

function canvasPoint(event) {
  const rect = els.editorCanvas.getBoundingClientRect();
  return {
    x: Math.max(0, Math.min(els.editorCanvas.width, (event.clientX - rect.left) * els.editorCanvas.width / rect.width)),
    y: Math.max(0, Math.min(els.editorCanvas.height, (event.clientY - rect.top) * els.editorCanvas.height / rect.height)),
  };
}

function normalizedSelection(start, end) {
  const x = Math.min(start.x, end.x);
  const y = Math.min(start.y, end.y);
  const width = Math.abs(end.x - start.x);
  const height = Math.abs(end.y - start.y);
  return { x, y, width, height };
}

function drawEditor() {
  if (!state.image) return;
  const canvas = els.editorCanvas;
  const ctx = canvas.getContext("2d");
  ctx.clearRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(state.image, 0, 0, canvas.width, canvas.height);
  const roi = state.selection;
  if (!roi || roi.width < 1 || roi.height < 1) return;

  ctx.save();
  ctx.fillStyle = "rgba(0, 0, 0, 0.55)";
  ctx.fillRect(0, 0, canvas.width, canvas.height);
  ctx.drawImage(
    state.image,
    roi.x, roi.y, roi.width, roi.height,
    roi.x, roi.y, roi.width, roi.height,
  );
  ctx.strokeStyle = "#69a7ff";
  ctx.lineWidth = Math.max(2, canvas.width / 320);
  ctx.setLineDash([12, 7]);
  ctx.strokeRect(roi.x, roi.y, roi.width, roi.height);
  ctx.restore();
}

function drawCropPreview() {
  const canvas = els.cropPreviewCanvas;
  const ctx = canvas.getContext("2d");
  const roi = state.selection;
  if (!state.image || !roi || roi.width < 1 || roi.height < 1) {
    canvas.width = 320;
    canvas.height = 180;
    ctx.fillStyle = "#020406";
    ctx.fillRect(0, 0, canvas.width, canvas.height);
    els.cropDimensions.textContent = "선택 없음";
    return;
  }
  const maxSide = 420;
  const scale = Math.min(1, maxSide / Math.max(roi.width, roi.height));
  canvas.width = Math.max(1, Math.round(roi.width * scale));
  canvas.height = Math.max(1, Math.round(roi.height * scale));
  ctx.drawImage(
    state.image,
    roi.x, roi.y, roi.width, roi.height,
    0, 0, canvas.width, canvas.height,
  );
  els.cropDimensions.textContent = `${Math.round(roi.width)} × ${Math.round(roi.height)} px · x=${Math.round(roi.x)}, y=${Math.round(roi.y)}`;
}

function updateSelectionDisplay() {
  drawEditor();
  drawCropPreview();
  updateDepthStats();
}

async function updateDepthStats() {
  const serial = ++state.statsRequestSerial;
  const roi = state.selection;
  if (!state.session || !roi || roi.width < 1 || roi.height < 1) {
    els.depthMedian.textContent = "-";
    els.depthRange.textContent = "-";
    els.depthValid.textContent = "-";
    return;
  }
  try {
    const payload = await api("/api/crop_stats", {
      method: "POST",
      body: { session_id: state.session.session_id, roi },
    });
    if (serial !== state.statsRequestSerial) return;
    const depth = payload.depth;
    if (!depth.available) {
      els.depthMedian.textContent = "Depth 없음";
      els.depthRange.textContent = "-";
      els.depthValid.textContent = "-";
      return;
    }
    els.depthMedian.textContent = formatMeters(depth.median_m);
    els.depthRange.textContent = depth.near_m == null
      ? "유효값 없음"
      : `${formatMeters(depth.near_m)} – ${formatMeters(depth.far_m)}`;
    els.depthValid.textContent = `${(depth.valid_ratio * 100).toFixed(1)}% (${depth.valid_count.toLocaleString()} px)`;
  } catch (error) {
    if (serial === state.statsRequestSerial) {
      els.depthMedian.textContent = "계산 실패";
      els.depthRange.textContent = "-";
      els.depthValid.textContent = "-";
    }
  }
}

function setFullFrame() {
  if (!state.image) return;
  state.selection = { x: 0, y: 0, width: state.image.naturalWidth, height: state.image.naturalHeight };
  updateSelectionDisplay();
}

function setCenterSquare() {
  if (!state.image) return;
  const side = Math.min(state.image.naturalWidth, state.image.naturalHeight) * 0.72;
  state.selection = {
    x: (state.image.naturalWidth - side) / 2,
    y: (state.image.naturalHeight - side) / 2,
    width: side,
    height: side,
  };
  updateSelectionDisplay();
}

function clearCrop() {
  state.selection = null;
  updateSelectionDisplay();
}

async function discardSession() {
  if (!state.session) return;
  setBusy(true, "버리는 중...", els.discardBtn);
  try {
    await api("/api/discard", {
      method: "POST",
      body: { session_id: state.session.session_id },
    });
    clearSessionUi();
    showToast("촬영 프레임을 버렸습니다.");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setBusy(false, "", els.discardBtn);
  }
}

function clearSessionUi() {
  state.session = null;
  state.image = null;
  state.selection = null;
  state.dragging = false;
  els.editorPanel.classList.add("hidden");
  els.notes.value = "";
}

async function saveCrop() {
  if (!state.session || !state.selection || state.selection.width < 1 || state.selection.height < 1) {
    showToast("저장할 크롭 영역을 선택하세요.", "error");
    return;
  }
  if (!validateIdentity()) return;

  const role = selectedRole();
  setBusy(true, "저장 중...", els.saveBtn);
  try {
    const payload = await api("/api/save", {
      method: "POST",
      body: {
        session_id: state.session.session_id,
        dataset_role: role,
        object_name: els.objectName.value.trim(),
        target_object: els.targetObject.value.trim(),
        view_label: els.viewLabel.value.trim() || "view",
        roi: state.selection,
        save_original: els.saveOriginal.checked,
        save_depth: els.saveDepth.checked,
        notes: els.notes.value,
      },
    });
    const display = {
      dataset_role: payload.dataset_role,
      reusable_for_all_targets: payload.reusable_for_all_targets,
      auto_negative_for_other_targets: payload.auto_negative_for_other_targets,
      paths: payload.paths,
      negative_sync: payload.negative_sync,
      next_step_wsl: "ros2 service call /embedding_retrieval/reload_banks std_srvs/srv/Trigger '{}'",
    };
    els.resultBox.textContent = JSON.stringify(display, null, 2);

    const successMessage = role === "positive"
      ? "등록 이미지를 저장했고 다른 목표의 negative 연결도 갱신했습니다."
      : role === "shared_negative"
        ? "공용 negative를 한 번 저장하고 모든 목표에 연결했습니다."
        : role === "background"
          ? "공용 background negative를 저장했습니다."
          : "목표 전용 hard negative를 저장했습니다.";
    showToast(successMessage, payload.negative_sync_error ? "error" : "success");
    if (payload.session_cleared) clearSessionUi();
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setBusy(false, "", els.saveBtn);
    applyRole(role, { rememberCurrent: false, setDefault: false });
  }
}

async function syncNegatives() {
  setBusy(true, "동기화 중...", els.syncNegativesBtn);
  try {
    const payload = await api("/api/sync_negatives", {
      method: "POST",
      body: {},
    });
    els.resultBox.textContent = JSON.stringify({
      negative_sync: payload.negative_sync,
      next_step_wsl: "ros2 service call /embedding_retrieval/reload_banks std_srvs/srv/Trigger '{}'",
    }, null, 2);
    showToast("등록 물체와 공용 negative의 자동 연결을 갱신했습니다.", "success");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setBusy(false, "", els.syncNegativesBtn);
  }
}

function setBusy(busy, label = "", activeButton = null) {
  state.busy = busy;
  els.captureBtn.disabled = busy || !state.cameraFresh;
  els.saveBtn.disabled = busy;
  els.discardBtn.disabled = busy;
  els.syncNegativesBtn.disabled = busy;

  if (activeButton && busy && label) {
    activeButton.dataset.previous = activeButton.textContent;
    activeButton.textContent = label;
  }
  if (activeButton && !busy && activeButton.dataset.previous) {
    activeButton.textContent = activeButton.dataset.previous;
    delete activeButton.dataset.previous;
  }
}

els.editorCanvas.addEventListener("pointerdown", (event) => {
  if (!state.image) return;
  event.preventDefault();
  els.editorCanvas.setPointerCapture(event.pointerId);
  state.dragging = true;
  state.dragStart = canvasPoint(event);
  state.selection = { x: state.dragStart.x, y: state.dragStart.y, width: 0, height: 0 };
  drawEditor();
});

els.editorCanvas.addEventListener("pointermove", (event) => {
  if (!state.dragging || !state.dragStart) return;
  event.preventDefault();
  state.selection = normalizedSelection(state.dragStart, canvasPoint(event));
  drawEditor();
  drawCropPreview();
});

function finishDrag(event) {
  if (!state.dragging) return;
  event.preventDefault();
  state.dragging = false;
  if (state.selection && (state.selection.width < 4 || state.selection.height < 4)) {
    state.selection = null;
  }
  updateSelectionDisplay();
}

els.editorCanvas.addEventListener("pointerup", finishDrag);
els.editorCanvas.addEventListener("pointercancel", finishDrag);
for (const input of els.roleInputs) {
  input.addEventListener("change", () => applyRole(input.value));
}
els.objectName.addEventListener("input", updateDestinationHint);
els.targetObject.addEventListener("input", updateDestinationHint);
els.captureBtn.addEventListener("click", captureFrame);
els.syncNegativesBtn.addEventListener("click", syncNegatives);
els.refreshStreamBtn.addEventListener("click", refreshLiveStream);
els.fullFrameBtn.addEventListener("click", setFullFrame);
els.centerSquareBtn.addEventListener("click", setCenterSquare);
els.clearCropBtn.addEventListener("click", clearCrop);
els.discardBtn.addEventListener("click", discardSession);
els.saveBtn.addEventListener("click", saveCrop);
window.addEventListener("resize", drawEditor);
els.liveImage.addEventListener("load", () => els.livePlaceholder.classList.add("hidden"));
els.liveImage.addEventListener("error", () => els.livePlaceholder.classList.remove("hidden"));

applyRole("positive", { rememberCurrent: false, setDefault: false });
refreshStatus();
window.setInterval(refreshStatus, 1200);
