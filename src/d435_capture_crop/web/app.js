"use strict";

const state = {
  session: null,
  image: null,
  selection: null,
  dragging: false,
  dragStart: null,
  statsRequestSerial: 0,
  toastTimer: null,
};

const $ = (id) => document.getElementById(id);
const els = {
  connectionBadge: $("connectionBadge"),
  liveImage: $("liveImage"),
  livePlaceholder: $("livePlaceholder"),
  objectName: $("objectName"),
  viewLabel: $("viewLabel"),
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
  state.toastTimer = window.setTimeout(() => els.toast.classList.add("hidden"), 4200);
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

async function refreshStatus() {
  try {
    const status = await api("/api/status");
    const age = status.color_age_sec;
    const fresh = status.color_available && Number.isFinite(age) && age < 2.0;
    els.connectionBadge.textContent = fresh
      ? `D435 연결됨 · Depth ${status.depth_available ? "있음" : "대기"}`
      : "D435 color 토픽 대기 중";
    els.connectionBadge.className = `badge ${fresh ? "badge-ok" : "badge-warn"}`;
    els.captureBtn.disabled = !fresh;
    els.livePlaceholder.classList.toggle("hidden", fresh && status.preview_available);

    if (!state.session && status.active_session) {
      await restoreSession(status.active_session);
    }
    if (!els.objectName.dataset.initialized && status.default_object_name) {
      els.objectName.value = status.default_object_name;
      els.saveOriginal.checked = Boolean(status.save_original_default);
      els.saveDepth.checked = Boolean(status.save_depth_default);
      els.objectName.dataset.initialized = "true";
    }
  } catch (error) {
    els.connectionBadge.textContent = "노드 연결 실패";
    els.connectionBadge.className = "badge badge-error";
    els.captureBtn.disabled = true;
  }
}

function refreshLiveStream() {
  els.liveImage.src = `/stream.mjpg?ts=${Date.now()}`;
}

async function captureFrame() {
  const objectName = els.objectName.value.trim();
  if (!objectName) {
    showToast("물체 이름을 입력하세요.", "error");
    els.objectName.focus();
    return;
  }
  setBusy(true, "촬영 중...");
  try {
    const payload = await api("/api/capture", {
      method: "POST",
      body: {
        object_name: objectName,
        view_label: els.viewLabel.value.trim() || "view",
      },
    });
    await loadSession(payload);
    showToast("프레임을 고정했습니다. 저장할 영역을 드래그하세요.", "success");
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setBusy(false);
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
  els.objectName.value = payload.object_name || els.objectName.value;
  els.viewLabel.value = payload.view_label || els.viewLabel.value;
  els.editorPanel.classList.remove("hidden");
  els.sessionBadge.textContent = `세션 ${payload.session_id.slice(0, 8)}`;
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
  try {
    await api("/api/discard", {
      method: "POST",
      body: { session_id: state.session.session_id },
    });
  } catch (error) {
    showToast(error.message, "error");
    return;
  }
  clearSessionUi();
  showToast("촬영 프레임을 버렸습니다.");
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
  setBusy(true, "저장 중...");
  try {
    const payload = await api("/api/save", {
      method: "POST",
      body: {
        session_id: state.session.session_id,
        object_name: els.objectName.value.trim(),
        view_label: els.viewLabel.value.trim() || "view",
        roi: state.selection,
        save_original: els.saveOriginal.checked,
        save_depth: els.saveDepth.checked,
        notes: els.notes.value,
      },
    });
    els.resultBox.textContent = JSON.stringify(payload.paths, null, 2);
    showToast("크롭 이미지와 메타데이터를 저장했습니다.", "success");
    if (payload.session_cleared) clearSessionUi();
  } catch (error) {
    showToast(error.message, "error");
  } finally {
    setBusy(false);
  }
}

function setBusy(busy, label = "", activeButton = els.saveBtn) {
  els.captureBtn.disabled = busy;
  els.saveBtn.disabled = busy;
  els.discardBtn.disabled = busy;

  if (busy && label) {
    activeButton.dataset.previous = activeButton.textContent;
    activeButton.textContent = label;
  }

  if (!busy && activeButton.dataset.previous) {
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
els.captureBtn.addEventListener("click", captureFrame);
els.refreshStreamBtn.addEventListener("click", refreshLiveStream);
els.fullFrameBtn.addEventListener("click", setFullFrame);
els.centerSquareBtn.addEventListener("click", setCenterSquare);
els.clearCropBtn.addEventListener("click", clearCrop);
els.discardBtn.addEventListener("click", discardSession);
els.saveBtn.addEventListener("click", saveCrop);
window.addEventListener("resize", drawEditor);
els.liveImage.addEventListener("load", () => els.livePlaceholder.classList.add("hidden"));
els.liveImage.addEventListener("error", () => els.livePlaceholder.classList.remove("hidden"));

refreshStatus();
window.setInterval(refreshStatus, 1200);
