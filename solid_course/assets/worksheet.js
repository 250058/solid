// 학습지 입력 자동 저장(localStorage) + JSON 내보내기/불러오기 + 초기화 + 인쇄 버튼(인쇄 시 details 펼침)
// 저장 키: 페이지 경로 + 입력칸 순번. 입력칸은 textarea/input/select/checkbox/radio.
(function () {
  const ns = "solid-ws:" + location.pathname.split("/").pop();
  const fields = () => Array.from(document.querySelectorAll("main textarea, main input, main select"));
  const key = (el, i) => ns + ":" + (el.dataset.k || el.name || i);
  function save() {
    fields().forEach((el, i) => {
      try {
        const v = (el.type === "checkbox" || el.type === "radio") ? el.checked : el.value;
        localStorage.setItem(key(el, i), JSON.stringify(v));
      } catch (e) {}
    });
    const s = document.querySelector(".saved");
    if (s) s.textContent = "자동 저장됨 " + new Date().toLocaleTimeString("ko-KR");
  }
  function load() {
    fields().forEach((el, i) => {
      try {
        const raw = localStorage.getItem(key(el, i));
        if (raw === null) return;
        const v = JSON.parse(raw);
        if (el.type === "checkbox" || el.type === "radio") el.checked = !!v; else el.value = v;
      } catch (e) {}
    });
  }
  const page = location.pathname.split("/").pop() || "index.html";
  const val = el => (el.type === "checkbox" || el.type === "radio") ? el.checked : el.value;
  const setVal = (el, v) => { if (el.type === "checkbox" || el.type === "radio") el.checked = !!v; else el.value = v == null ? "" : v; };
  // JSON 내보내기: { format, page, savedAt, fields: { 입력칸키: 값 } }
  function exportJson() {
    const data = { format: "solid-worksheet", version: 1, page: page, savedAt: new Date().toISOString(), fields: {} };
    fields().forEach((el, i) => { data.fields[el.dataset.k || el.name || String(i)] = val(el); });
    // 파일명은 고정(학습지당 파일 하나): session_1_학번_이름.json. 다시 저장하면 같은 이름으로 내려받는다.
    const safe = v => String(v || "").trim().replace(/[\\/:*?"<>|\s]+/g, "");
    const who = [safe(data.fields["id-no"]), safe(data.fields["id-name"])].filter(Boolean).join("_");
    const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
    const a = document.createElement("a");
    a.href = URL.createObjectURL(blob);
    a.download = page.replace(/\.html$/, "") + (who ? "_" + who : "") + ".json";
    document.body.appendChild(a); a.click(); a.remove();
    setTimeout(() => URL.revokeObjectURL(a.href), 1000);
  }
  // JSON 불러오기: 검증 후 현재 입력을 덮어쓴다.
  function importJson(file) {
    const status = msg => { const s = document.querySelector(".saved"); if (s) s.textContent = msg; };
    const r = new FileReader();
    r.onerror = () => alert("파일을 읽지 못했습니다.");
    r.onload = () => {
      let data;
      try { data = JSON.parse(r.result); } catch (e) { alert("JSON 형식이 올바르지 않습니다."); return; }
      if (!data || data.format !== "solid-worksheet" || typeof data.fields !== "object" || data.fields === null) {
        alert("이 학습지에서 저장한 JSON 파일이 아닙니다."); return;
      }
      if (data.page !== page && !confirm("이 파일은 '" + data.page + "' 학습지의 저장본입니다. 현재 '" + page + "'에 불러올까요? (이름이 같은 칸만 채워집니다)")) return;
      if (!confirm("현재 입력을 불러온 내용으로 덮어쓸까요?")) return;
      let n = 0;
      fields().forEach((el, i) => {
        const k = el.dataset.k || el.name || String(i);
        if (Object.prototype.hasOwnProperty.call(data.fields, k)) { setVal(el, data.fields[k]); n++; }
      });
      save();
      status(n + "칸을 불러왔습니다 (" + (data.savedAt ? data.savedAt.slice(0, 16).replace("T", " ") : "") + " 저장본)");
    };
    r.readAsText(file);
  }
  document.addEventListener("DOMContentLoaded", () => {
    load();
    document.addEventListener("input", save);
    document.addEventListener("change", save);
    const bar = document.createElement("div");
    bar.className = "ws-tools";
    bar.innerHTML = '<span class="saved"></span><button type="button" id="ws-export">💾 JSON 저장</button><button type="button" id="ws-import">📂 JSON 불러오기</button><input type="file" id="ws-file" accept="application/json,.json" hidden><button type="button" id="ws-print">🖨 인쇄/PDF</button><button type="button" id="ws-reset">입력 지우기</button>';
    document.body.appendChild(bar);
    document.getElementById("ws-export").onclick = exportJson;
    const fileInput = document.getElementById("ws-file");
    document.getElementById("ws-import").onclick = () => fileInput.click();
    fileInput.onchange = () => { if (fileInput.files[0]) importJson(fileInput.files[0]); fileInput.value = ""; };
    document.getElementById("ws-print").onclick = () => window.print();
    // 인쇄할 때는 접힌 details(정의 확인 등)를 모두 펼쳤다가, 인쇄가 끝나면 원래 상태로 되돌린다.
    // 힌트(details.hint)는 worksheet.css의 @media print 규칙으로 인쇄에서 계속 숨겨진다.
    let wasClosed = [];
    window.addEventListener("beforeprint", () => {
      wasClosed = Array.from(document.querySelectorAll("details:not([open])"));
      wasClosed.forEach(d => { d.open = true; });
    });
    window.addEventListener("afterprint", () => {
      wasClosed.forEach(d => { d.open = false; });
      wasClosed = [];
    });
    document.getElementById("ws-reset").onclick = () => {
      if (!confirm("이 학습지의 입력을 모두 지울까요?")) return;
      fields().forEach((el, i) => { try { localStorage.removeItem(key(el, i)); } catch (e) {} });
      fields().forEach(el => { if (el.type === "checkbox" || el.type === "radio") el.checked = false; else el.value = ""; });
    };
  });
})();
