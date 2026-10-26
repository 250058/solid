/* 교재·학습지 옆에 붙는 Python 실행창.
   - Alt+P를 누르면 오른쪽에서 실행창이 나오고, 다시 누르면 들어간다(실행창 안에서는 Esc로도 닫힌다).
   - Pyodide(브라우저에서 도는 파이썬)를 실행창을 처음 열 때 미리 불러온다.
   - 편집기는 uml-tool의 Python 실행창과 같은 방식이다: VS Code "2026 Dark" 배색의 구문 강조,
     줄 번호, 현재 줄·들여쓰기 안내선, 자동완성, 괄호 자동 닫기, VS Code 단축키, 직접 구현한 실행취소.
   - 여기에 더해: input() 입력창, 오류 난 줄로 이동, 출력 복사, 실행창 너비·출력 높이 조절, 단축키 도움말,
     '이 페이지 코드' 목록에서 본문 코드 가져오기.
   - 편집 중인 코드는 페이지마다, 글자 크기·칸 크기는 모든 페이지에 공통으로 브라우저에 저장된다. */
(function () {
  // 실행창 스타일은 이 스크립트 옆의 pyrunner.css에 있다. 페이지는 <script> 한 줄만 넣으면 된다.
  const CSS_URL = new URL('pyrunner.css', document.currentScript.src).href;
  const BUNDLE_URL = new URL('code_bundle.js', document.currentScript.src).href;
  const PYODIDE_URL = 'https://cdn.jsdelivr.net/pyodide/v314.0.7/full/';
  const MYPY_SPEC = 'mypy==2.4.0';   // 최신 mypy (Pyodide 314용 wasm 휠이 있는 버전)
  const HLJS_URL = 'https://cdnjs.cloudflare.com/ajax/libs/highlight.js/11.9.0/highlight.min.js';
  const KEY = {
    draft: 'pyrunner-draft:' + location.pathname,
    font: 'pyrunner-fontsize',
    outH: 'pyrunner-output-height',
    width: 'pyrunner-width',
    theme: 'pyrunner-theme',
  };
  const DEFAULT_CODE =
    '# 여기에 파이썬 코드를 쓰고 Ctrl+Enter(또는 F5)로 실행하세요.\n' +
    '# 위쪽 목록에서 이 페이지의 코드를 가져올 수 있습니다. 단축키는 ? 버튼에 있습니다.\n' +
    '\n' +
    'name = input("이름을 입력하세요: ")\n' +
    'print(f"안녕하세요, {name}님!")\n';
  // Python 로고(투명 배경 SVG)
  const LOGO = '<svg class="pr-logo" viewBox="0 0 256 255" aria-hidden="true">' +
    '<path fill="#3776AB" d="M126.916.072c-64.832 0-60.784 28.115-60.784 28.115l.072 29.128h61.868v8.745H41.631S.145 61.355.145 126.77c0 65.417 36.21 63.097 36.21 63.097h21.61v-30.356s-1.165-36.21 35.632-36.21h61.362s34.475.557 34.475-33.319V33.97S194.67.072 126.916.072zM92.802 19.66a11.12 11.12 0 0 1 11.13 11.13 11.12 11.12 0 0 1-11.13 11.13 11.12 11.12 0 0 1-11.13-11.13 11.12 11.12 0 0 1 11.13-11.13z"/>' +
    '<path fill="#FFD43B" d="M128.757 254.126c64.832 0 60.784-28.115 60.784-28.115l-.072-29.127H127.6v-8.745h86.441s41.486 4.705 41.486-60.712c0-65.416-36.21-63.096-36.21-63.096h-21.61v30.355s1.165 36.21-35.632 36.21h-61.362s-34.475-.557-34.475 33.32v56.013s-5.235 33.897 62.518 33.897zm34.114-19.586a11.12 11.12 0 0 1-11.13-11.13 11.12 11.12 0 0 1 11.13-11.131 11.12 11.12 0 0 1 11.13 11.13 11.12 11.12 0 0 1-11.13 11.13z"/>' +
    '</svg>';
  const SHORTCUTS = [
    ['Alt+P', '실행창 열기/닫기 (안에서는 Esc도 가능)'],
    ['Ctrl+Enter / F5', '실행'],
    ['Ctrl+Shift+Enter / F8', 'mypy 타입 검사'],
    ['Ctrl+Shift+I', '빠진 import 자동 추가'],
    ['Ctrl+K', '출력 지우기'],
    ['Ctrl+S / Ctrl+O', '.py 파일로 저장 / 불러오기'],
    ['Ctrl+Z / Ctrl+Y', '실행취소 / 다시 실행 (Ctrl+Shift+Z도 가능)'],
    ['Tab / Shift+Tab', '들여쓰기 / 내어쓰기 (여러 줄 선택 가능)'],
    ['Ctrl+] / Ctrl+[', '들여쓰기 / 내어쓰기'],
    ['Ctrl+/', '주석 켜기/끄기'],
    ['Ctrl+D', '현재 줄 복제'],
    ['Ctrl+Shift+K', '현재 줄 삭제'],
    ['Alt+↑ / Alt+↓', '현재 줄 위/아래로 옮기기'],
    ['Shift+Alt+↑ / ↓', '현재 줄 위/아래로 복사'],
    ['Ctrl+Backspace', '앞 단어 지우기'],
    ['Ctrl+Shift+\\', '짝 괄호로 이동'],
    ['Home', '줄의 첫 글자 ↔ 줄 맨 앞'],
    ['Ctrl+Space', '자동완성 열기 (↑↓ 고르기, Enter/Tab 넣기, Esc 닫기)'],
    ['Ctrl+= / Ctrl+-', '글자 크기 키우기 / 줄이기'],
  ];

  // 편집기 테마. 'auto'는 교재 테마(밝게/어둡게)를 따른다. 색은 pyrunner.css의 [data-pr-theme]에 있다.
  const THEMES = [
    ['auto', '테마: 자동'],
    ['light', 'GitHub Light'],
    ['dark', 'VS Code Dark'],
    ['solarized-light', 'Solarized Light'],
    ['one-dark', 'One Dark'],
    ['monokai', 'Monokai'],
    ['dracula', 'Dracula'],
    ['nord', 'Nord'],
    ['high-contrast', '고대비'],
  ];

  let pyodidePromise = null;
  let running = false;
  let fontSize = 13;
  let errorLines = new Set();   // 오류(실행·mypy)가 난 줄 번호: 줄 번호 칸에 빨갛게 표시
  let mypyPromise = null;
  let el = {};
  let saveTimer = null;

  const $ = (sel) => el.panel.querySelector(sel);
  const store = {
    get(k) { try { return localStorage.getItem(k); } catch (e) { return null; } },
    set(k, v) { try { localStorage.setItem(k, v); } catch (e) { /* 저장소를 못 써도 동작은 한다 */ } },
  };

  /* =========================================================
     Pyodide · highlight.js 불러오기
     ========================================================= */
  function loadScript(src) {
    return new Promise((resolve, reject) => {
      const s = document.createElement('script');
      s.src = src;
      s.onload = resolve;
      s.onerror = () => reject(new Error(src + ' 를 불러오지 못했습니다 (인터넷 연결을 확인하세요).'));
      document.head.appendChild(s);
    });
  }

  function loadPyodideOnce() {
    if (pyodidePromise) return pyodidePromise;
    pyodidePromise = (async () => {
      if (!window.loadPyodide) await loadScript(PYODIDE_URL + 'pyodide.js');
      return window.loadPyodide({ indexURL: PYODIDE_URL });
    })();
    pyodidePromise.catch(() => { pyodidePromise = null; });
    return pyodidePromise;
  }

  /* =========================================================
     본문 코드 블록 찾기 ('이 페이지 코드 가져오기' 목록)
     ========================================================= */
  // 퀴즈 밖의 코드 블록 중 '실행 결과' 출력, 화살표 그림, 줄 번호가 붙은 읽기용 코드는 뺀다.
  function pageBlocks() {
    return Array.from(document.querySelectorAll('main pre > code')).filter((code) => {
      if (code.closest('.quiz, #pyrunner')) return false;
      const prev = code.parentElement.previousElementSibling;
      if (prev && /^실행 결과/.test(prev.textContent.trim())) return false;
      if (/[─│▶]/.test(code.textContent) && !/\b(def|class|import)\b/.test(code.textContent)) return false;
      if (/^\d+\s{2}/.test(code.textContent.trim())) return false;
      return true;
    });
  }

  function blockLabel(code, i) {
    // 학습지는 활동 제목(h3), 교재는 절 제목(h2)
    const activity = code.closest('.activity');
    const section = code.closest('section');
    const head = (activity && activity.querySelector('h3')) || (section && section.querySelector('h2'));
    const text = code.textContent;
    // '# ===== 제목 =====' 줄이 있으면 그 제목, import만 있는 파일 상단이면 그렇게, 아니면 첫 클래스 이름
    const first = text.split('\n').find((l) => /^#\s*=+\s*[^=\s]/.test(l));
    const title = first ? first.replace(/^#\s*=+\s*|\s*=+\s*$/g, '')
      : (text.trim().startsWith('"""') && !/\bclass\s/.test(text)) ? '파일 상단 (설명·import)'
      : (text.match(/\bclass\s+(\w+)/) || [, ''])[1];
    return (i + 1) + '. ' + (head ? head.textContent.trim() : '코드') + (title ? ' — ' + title.slice(0, 40) : '');
  }

  /* =========================================================
     실행창 만들기
     ========================================================= */
  function build() {
    const link = document.createElement('link');
    link.rel = 'stylesheet';
    link.href = CSS_URL;
    document.head.appendChild(link);

    el.panel = document.createElement('aside');
    el.panel.id = 'pyrunner';
    el.panel.setAttribute('aria-hidden', 'true');
    el.panel.innerHTML =
      '<div class="pr-wresize" title="끌어서 실행창 너비 조절"></div>' +
      '<div class="pr-head">' +
        LOGO + '<b>Python 실행창</b>' +
        '<select class="pr-theme" title="편집기 테마">' +
          THEMES.map(([v, label]) => '<option value="' + v + '">' + label + '</option>').join('') +
        '</select>' +
        '<span class="pr-font"><button type="button" data-f="-1" title="글자 작게 (Ctrl+-)">−</button>' +
        '<span class="pr-fontlabel">13px</span><button type="button" data-f="1" title="글자 크게 (Ctrl+=)">+</button></span>' +
        '<button type="button" class="pr-icon pr-helpbtn" title="단축키 보기">?</button>' +
        '<button type="button" class="pr-icon pr-close" title="닫기 (Alt+P)">✕</button>' +
      '</div>' +
      '<div class="pr-tools">' +
        '<select class="pr-pick"><option value="">코드 가져오기…</option></select>' +
        '<button type="button" class="pr-btn pr-primary pr-run" title="실행 (Ctrl+Enter / F5)">▶ 실행</button>' +
        '<button type="button" class="pr-btn pr-mypy" title="mypy 타입 검사 (Ctrl+Shift+Enter / F8)">mypy<span class="pr-long"> 검사</span></button>' +
        '<button type="button" class="pr-btn pr-clearout" title="출력 지우기 (Ctrl+K)"><span class="pr-long">출력 </span>지우기</button>' +
        '<button type="button" class="pr-btn pr-save" title=".py로 저장 (Ctrl+S)">저장</button>' +
        '<button type="button" class="pr-btn pr-open" title=".py 불러오기 (Ctrl+O)">불러오기</button>' +
        '<button type="button" class="pr-btn pr-reset" title="편집기 비우기">초기화</button>' +
      '</div>' +
      '<div class="pr-help" hidden><table>' +
        SHORTCUTS.map(([k, d]) => '<tr><th>' + k + '</th><td>' + d + '</td></tr>').join('') +
      '</table></div>' +
      '<div class="pr-body">' +
        '<div class="pr-editor-wrap">' +
          '<div class="pr-gutter">1</div>' +
          '<div class="pr-code-wrap">' +
            '<div class="pr-curline"></div>' +
            '<div class="pr-guides"></div>' +
            // 구문 강조: 글자가 투명한 textarea 밑에 색칠된 <pre>를 겹쳐 둔다.
            '<pre class="pr-hl" aria-hidden="true"><code class="language-python"></code></pre>' +
            '<textarea class="pr-editor" spellcheck="false" autocapitalize="off" autocomplete="off" autocorrect="off" wrap="off"></textarea>' +
          '</div>' +
        '</div>' +
        '<div class="pr-resize" title="끌어서 출력 칸 높이 조절"></div>' +
        '<div class="pr-outwrap">' +
          '<div class="pr-outhead"><span>출력 (OUTPUT)</span><span class="pr-status"></span>' +
          '<button type="button" class="pr-copy" title="출력 복사">복사</button></div>' +
          '<pre class="pr-out"></pre>' +
        '</div>' +
      '</div>';
    document.body.appendChild(el.panel);

    el.ac = document.createElement('div');
    el.ac.className = 'pr-ac';
    document.body.appendChild(el.ac);

    el.ta = $('.pr-editor');
    el.hlPre = $('.pr-hl');
    el.hlCode = el.hlPre.firstChild;
    el.gutter = $('.pr-gutter');
    el.curline = $('.pr-curline');
    el.guides = $('.pr-guides');
    el.out = $('.pr-out');
    el.outWrap = $('.pr-outwrap');
    el.status = $('.pr-status');
    el.run = $('.pr-run');

    buildPicker();

    el.ta.value = store.get(KEY.draft) || DEFAULT_CODE;
    hist.last = el.ta.value;
    const savedFont = parseInt(store.get(KEY.font), 10);
    applyFontSize(savedFont || 13, false);
    const savedH = parseInt(store.get(KEY.outH), 10);
    if (savedH) el.outWrap.style.flexBasis = savedH + 'px';
    const savedW = parseInt(store.get(KEY.width), 10);
    if (savedW) setWidth(savedW, false);

    el.ta.addEventListener('input', () => { refresh(); scheduleSave(); scheduleHist(); updateAutocomplete(); });
    el.ta.addEventListener('scroll', () => { syncScroll(); hideAutocomplete(); });
    el.ta.addEventListener('keydown', onEditorKey);
    el.ta.addEventListener('keyup', updateCurrentLine);
    el.ta.addEventListener('click', () => { updateCurrentLine(); hideAutocomplete(); });
    el.ta.addEventListener('focus', updateCurrentLine);
    el.ta.addEventListener('blur', () => setTimeout(hideAutocomplete, 100));

    el.run.addEventListener('click', run);
    $('.pr-clearout').addEventListener('click', clearOutput);
    $('.pr-save').addEventListener('click', saveFile);
    $('.pr-open').addEventListener('click', openFile);
    $('.pr-reset').addEventListener('click', resetEditor);
    $('.pr-mypy').addEventListener('click', runMypy);
    const themeSel = $('.pr-theme');
    themeSel.value = store.get(KEY.theme) || 'auto';
    applyTheme(themeSel.value);
    themeSel.addEventListener('change', () => { applyTheme(themeSel.value); store.set(KEY.theme, themeSel.value); el.ta.focus(); });
    $('.pr-close').addEventListener('click', () => toggle(false));
    $('.pr-helpbtn').addEventListener('click', () => { const h = $('.pr-help'); h.hidden = !h.hidden; });
    $('.pr-copy').addEventListener('click', copyOutput);
    el.panel.querySelectorAll('.pr-font button').forEach((b) =>
      b.addEventListener('click', () => applyFontSize(fontSize + Number(b.dataset.f))));
    el.out.addEventListener('click', (e) => {
      const jump = e.target.closest('[data-line]');
      if (jump) goToLine(Number(jump.dataset.line));
    });
    bindOutputResize($('.pr-resize'));
    bindWidthResize($('.pr-wresize'));
    document.addEventListener('mousedown', (e) => {
      if (el.ac.classList.contains('show') && !el.ac.contains(e.target) && e.target !== el.ta) hideAutocomplete();
    });

    loadScript(HLJS_URL).then(refresh, () => { /* 강조 없이도 편집은 된다 */ });
    refresh();
  }

  // 목록: [이 페이지 코드] 본문 코드 블록 + [학습지 시작 코드]·[교재 예제 코드] .py 파일(code_bundle.js)
  function buildPicker() {
    const picker = $('.pr-pick');
    const blocks = pageBlocks();
    let files = [];
    if (blocks.length) {
      const group = document.createElement('optgroup');
      group.label = '이 페이지 코드';
      blocks.forEach((code, i) => group.appendChild(new Option(blockLabel(code, i), 'b' + i)));
      // 교재(장)처럼 블록들이 한 파일을 이루는 페이지에서만. 학습지의 코드 조각은 서로 별개다.
      if (blocks.length > 1 && !document.querySelector('.activity')) {
        group.appendChild(new Option('본문 코드 전부 이어 붙이기 (바로 실행 가능)', 'all'));
      }
      picker.appendChild(group);
    }
    // .py 파일 묶음은 tools/build_code_bundle.py가 만든다. 파일을 추가하면 목록에도 저절로 생긴다.
    loadScript(BUNDLE_URL).then(() => {
      files = window.PYRUNNER_FILES || [];
      const groups = {};
      files.forEach((f, i) => {
        if (!groups[f.group]) {
          groups[f.group] = document.createElement('optgroup');
          groups[f.group].label = f.group;
          picker.appendChild(groups[f.group]);
        }
        groups[f.group].appendChild(new Option(f.name + (f.title ? ' — ' + f.title.slice(0, 50) : ''), 'f' + i));
      });
    }, () => { /* 묶음 파일이 없으면 이 페이지 코드만 보여 준다 */ });
    picker.addEventListener('change', () => {
      const v = picker.value;
      if (!v) return;
      let text;
      if (v === 'all') text = blocks.map((c) => c.textContent.replace(/\s+$/, '')).join('\n\n\n');
      else if (v[0] === 'f') text = files[Number(v.slice(1))].code.replace(/\s+$/, '');
      else text = blocks[Number(v.slice(1))].textContent.replace(/\s+$/, '');
      // 학습지·교재의 코드 조각은 import 줄이 빠진 경우가 많아 불러올 때 채워 넣는다.
      setCode(addMissingImports(text + '\n'));
      setStatus(picker.options[picker.selectedIndex].text.split(' — ')[0] + ' 불러옴', 'ok');
      picker.value = '';
      el.ta.focus();
    });
  }

  /* =========================================================
     열고 닫기 · 크기 조절
     ========================================================= */
  function isOpen() { return document.body.classList.contains('pr-open'); }

  function toggle(force) {
    const open = force === undefined ? !isOpen() : force;
    document.body.classList.toggle('pr-open', open);
    el.panel.setAttribute('aria-hidden', String(!open));
    if (open) {
      el.ta.focus();
      refresh();
      loadPyodideOnce().catch(() => { /* 실행할 때 다시 시도하고 오류를 보여 준다 */ });
    } else {
      hideAutocomplete();
      if (document.activeElement && el.panel.contains(document.activeElement)) document.activeElement.blur();
    }
  }

  function setWidth(w, save) {
    const px = Math.max(400, Math.min(window.innerWidth - 120, Math.round(w)));
    document.documentElement.style.setProperty('--pr-w', px + 'px');
    if (save !== false) store.set(KEY.width, String(px));
  }

  function bindWidthResize(handle) {
    handle.addEventListener('pointerdown', (e) => {
      e.preventDefault();
      handle.classList.add('dragging');
      document.body.classList.add('pr-dragging');
      const move = (ev) => setWidth(window.innerWidth - ev.clientX, false);
      const up = () => {
        handle.classList.remove('dragging');
        document.body.classList.remove('pr-dragging');
        window.removeEventListener('pointermove', move);
        window.removeEventListener('pointerup', up);
        setWidth(el.panel.getBoundingClientRect().width);
        refresh();
      };
      window.addEventListener('pointermove', move);
      window.addEventListener('pointerup', up);
    });
  }

  function bindOutputResize(handle) {
    handle.addEventListener('pointerdown', (e) => {
      e.preventDefault();
      const startY = e.clientY;
      const startH = el.outWrap.getBoundingClientRect().height;
      handle.classList.add('dragging');
      document.body.classList.add('pr-dragging');
      const move = (ev) => {
        const max = $('.pr-body').clientHeight - 80;
        el.outWrap.style.flexBasis = Math.max(60, Math.min(max, startH - (ev.clientY - startY))) + 'px';
        syncScroll();
      };
      const up = () => {
        handle.classList.remove('dragging');
        document.body.classList.remove('pr-dragging');
        window.removeEventListener('pointermove', move);
        window.removeEventListener('pointerup', up);
        store.set(KEY.outH, String(Math.round(el.outWrap.getBoundingClientRect().height)));
      };
      window.addEventListener('pointermove', move);
      window.addEventListener('pointerup', up);
    });
  }

  /* =========================================================
     편집기 화면: 구문 강조 · 줄 번호 · 들여쓰기 안내선 · 현재 줄
     ========================================================= */
  function lineHeight() { return fontSize + 7; }   // 13px 글자에 20px 줄 높이 비율 유지
  let charWidthCache = null;
  function charWidth() {
    if (charWidthCache) return charWidthCache;
    const span = document.createElement('span');
    span.style.cssText = 'position:absolute;visibility:hidden;white-space:pre;font:' + fontSize + "px Consolas,'Cascadia Mono','D2Coding',monospace";
    span.textContent = '0000000000';
    document.body.appendChild(span);
    charWidthCache = span.getBoundingClientRect().width / 10 || fontSize * 0.6;
    span.remove();
    return charWidthCache;
  }

  function applyFontSize(size, save) {
    fontSize = Math.max(10, Math.min(28, Math.round(size)));
    el.panel.style.setProperty('--pr-font', fontSize + 'px');
    el.panel.style.setProperty('--pr-line', lineHeight() + 'px');
    charWidthCache = null;
    $('.pr-fontlabel').textContent = fontSize + 'px';
    if (save !== false) store.set(KEY.font, String(fontSize));
    refresh();
  }

  function escapeHtml(s) { return s.replace(/[&<>]/g, (c) => ({ '&': '&amp;', '<': '&lt;', '>': '&gt;' }[c])); }

  function refresh() {
    const value = el.ta.value;
    // 마지막 줄이 빈 줄이어도 높이가 맞도록 줄바꿈 하나를 더 붙인다.
    el.hlCode.textContent = value + '\n';
    if (window.hljs) {
      delete el.hlCode.dataset.highlighted;
      try {
        window.hljs.highlightElement(el.hlCode);
        // 주석 안의 TODO/FIXME만 따로 강조
        el.hlCode.querySelectorAll('.hljs-comment').forEach((c) => {
          c.innerHTML = c.innerHTML.replace(/\b(TODO|FIXME)\b/g, '<span class="pr-todo">$1</span>');
        });
      } catch (e) { /* 강조 실패해도 편집은 된다 */ }
    }
    const lines = value.split('\n');
    el.gutter.innerHTML = lines.map((_, i) =>
      (errorLines.has(i + 1) ? '<span class="pr-errline">' + (i + 1) + '</span>' : String(i + 1))).join('\n') + '\n';
    updateGuides(lines);
    syncScroll();
  }

  // VS Code처럼 들여쓰기 4칸마다 옅은 세로 안내선
  function updateGuides(lines) {
    const cw = charWidth(), lh = lineHeight();
    let html = '';
    lines.forEach((line, i) => {
      const levels = Math.floor(line.match(/^ */)[0].length / 4);
      for (let lvl = 0; lvl < levels; lvl++) {
        html += '<span style="left:' + (12 + lvl * 4 * cw) + 'px;top:' + (i * lh + 10) + 'px;height:' + lh + 'px"></span>';
      }
    });
    el.guides.innerHTML = html;
  }

  function syncScroll() {
    const t = el.ta;
    el.hlPre.scrollTop = t.scrollTop;
    el.hlPre.scrollLeft = t.scrollLeft;
    el.gutter.scrollTop = t.scrollTop;
    el.guides.style.transform = 'translate(' + (-t.scrollLeft) + 'px,' + (-t.scrollTop) + 'px)';
    updateCurrentLine();
  }

  function updateCurrentLine() {
    const t = el.ta;
    const idx = t.value.slice(0, t.selectionStart).split('\n').length - 1;
    el.curline.style.height = lineHeight() + 'px';
    el.curline.style.top = (idx * lineHeight() + 10 - t.scrollTop) + 'px';
  }

  // 코드로 커서를 옮기면 브라우저가 스크롤해 주지 않으므로 커서 줄이 보이게 직접 맞춘다.
  function scrollCaretIntoView() {
    const t = el.ta, lh = lineHeight();
    const idx = t.value.slice(0, t.selectionStart).split('\n').length - 1;
    const top = idx * lh + 10, bottom = top + lh;
    if (top < t.scrollTop) t.scrollTop = Math.max(0, top - lh);
    else if (bottom > t.scrollTop + t.clientHeight) t.scrollTop = bottom - t.clientHeight + lh;
  }

  // 키 처리로 내용을 바꾼 뒤 공통으로 부른다.
  function afterEdit() {
    errorLines.clear();
    refresh();
    scrollCaretIntoView();
    syncScroll();
    scheduleSave();
    scheduleHist();
  }

  function scheduleSave() {
    clearTimeout(saveTimer);
    saveTimer = setTimeout(() => store.set(KEY.draft, el.ta.value), 400);
  }

  function setCode(text) {
    histTrack();
    el.ta.value = text;
    el.ta.selectionStart = el.ta.selectionEnd = 0;
    el.ta.scrollTop = 0;
    afterEdit();
    histTrack();
  }

  /* =========================================================
     실행취소/다시 실행 — 브라우저마다 다른 textarea 기본 undo 대신 직접 구현
     ========================================================= */
  const hist = { past: [], future: [], last: null };
  let histTimer = null;
  function histTrack() {
    const snap = el.ta.value;
    if (snap === hist.last) return;
    hist.past.push(hist.last);
    if (hist.past.length > 300) hist.past.shift();
    hist.future.length = 0;
    hist.last = snap;
  }
  function scheduleHist() { clearTimeout(histTimer); histTimer = setTimeout(histTrack, 400); }
  function undo() {
    clearTimeout(histTimer); histTrack();
    if (!hist.past.length) return;
    hist.future.push(hist.last);
    hist.last = hist.past.pop();
    el.ta.value = hist.last;
    refresh(); store.set(KEY.draft, el.ta.value);
  }
  function redo() {
    clearTimeout(histTimer); histTrack();
    if (!hist.future.length) return;
    hist.past.push(hist.last);
    hist.last = hist.future.pop();
    el.ta.value = hist.last;
    refresh(); store.set(KEY.draft, el.ta.value);
  }

  /* =========================================================
     편집 동작들 (VS Code 기준)
     ========================================================= */
  function lineBounds(t) {
    const v = t.value, s = t.selectionStart, e = t.selectionEnd;
    const start = v.lastIndexOf('\n', s - 1) + 1;
    let end = v.indexOf('\n', e > s ? e - 1 : e);
    if (end === -1) end = v.length;
    return { start, end };
  }
  function curLine(t) {
    const v = t.value, pos = t.selectionStart;
    const start = v.lastIndexOf('\n', pos - 1) + 1;
    let end = v.indexOf('\n', pos);
    if (end === -1) end = v.length;
    return { start, end, pos, text: v.slice(start, end) };
  }

  function indent(t, dedent) {
    if (!dedent && t.selectionStart === t.selectionEnd) { t.setRangeText('    ', t.selectionStart, t.selectionEnd, 'end'); return; }
    const { start, end } = lineBounds(t);
    const lines = t.value.slice(start, end).split('\n').map((l) => (dedent ? l.replace(/^( {1,4}|\t)/, '') : '    ' + l));
    t.setRangeText(lines.join('\n'), start, end, 'select');
  }
  function toggleComment(t) {
    const { start, end } = lineBounds(t);
    const lines = t.value.slice(start, end).split('\n');
    const code = lines.filter((l) => l.trim());
    const all = code.length > 0 && code.every((l) => /^\s*#/.test(l));
    const out = lines.map((l) => (!l.trim() ? l : all ? l.replace(/^(\s*)#\s?/, '$1') : l.replace(/^(\s*)/, '$1# ')));
    t.setRangeText(out.join('\n'), start, end, 'select');
  }
  function duplicateLine(t) {
    const { end, text } = curLine(t);
    t.setRangeText('\n' + text, end, end, 'end');
  }
  function deleteLine(t) {
    const v = t.value, { start, end } = curLine(t);
    const delEnd = end < v.length ? end + 1 : end;
    const delStart = (delEnd === end && start > 0) ? start - 1 : start;
    t.setRangeText('', delStart, delEnd, 'end');
  }
  function moveLine(t, dir) {
    const v = t.value, { start, end, pos, text } = curLine(t);
    const offset = pos - start;
    if (dir < 0) {
      if (start === 0) return;
      const prevStart = v.lastIndexOf('\n', start - 2) + 1;
      const prev = v.slice(prevStart, start - 1);
      t.setRangeText(text + '\n' + prev, prevStart, end, 'end');
      t.selectionStart = t.selectionEnd = prevStart + offset;
    } else {
      if (end === v.length) return;
      let nextEnd = v.indexOf('\n', end + 1);
      if (nextEnd === -1) nextEnd = v.length;
      const next = v.slice(end + 1, nextEnd);
      t.setRangeText(next + '\n' + text, start, nextEnd, 'end');
      t.selectionStart = t.selectionEnd = start + next.length + 1 + offset;
    }
  }
  function copyLine(t, dir) {
    const { start, end, pos, text } = curLine(t);
    const offset = pos - start;
    if (dir < 0) {
      t.setRangeText(text + '\n', start, start, 'end');
      t.selectionStart = t.selectionEnd = start + offset;
    } else {
      t.setRangeText('\n' + text, end, end, 'end');
      t.selectionStart = t.selectionEnd = end + 1 + offset;
    }
  }
  function smartHome(t, extend) {
    const { start, pos, text } = curLine(t);
    const first = start + text.match(/^[ \t]*/)[0].length;
    const target = pos === first ? start : first;
    if (extend) t.selectionEnd = target;
    else t.selectionStart = t.selectionEnd = target;
  }
  function jumpToBracket(t) {
    const pairs = { '(': ')', '[': ']', '{': '}' }, rev = { ')': '(', ']': '[', '}': '{' };
    const v = t.value;
    let i = t.selectionStart, open, close, dir;
    if (pairs[v[i]]) { open = v[i]; close = pairs[open]; dir = 1; }
    else if (pairs[v[i - 1]]) { i--; open = v[i]; close = pairs[open]; dir = 1; }
    else if (rev[v[i - 1]]) { i--; close = v[i]; open = rev[close]; dir = -1; }
    else if (rev[v[i]]) { close = v[i]; open = rev[close]; dir = -1; }
    else return;
    let depth = 0;
    for (let j = i; j >= 0 && j < v.length; j += dir) {
      if (v[j] === (dir > 0 ? open : close)) depth++;
      else if (v[j] === (dir > 0 ? close : open) && --depth === 0) {
        t.selectionStart = t.selectionEnd = dir > 0 ? j + 1 : j;
        return;
      }
    }
  }
  function handleEnter(t, e) {
    if (t.selectionStart !== t.selectionEnd) return false;
    const v = t.value, pos = t.selectionStart;
    const line = v.slice(v.lastIndexOf('\n', pos - 1) + 1, pos);
    let ind = line.match(/^[ \t]*/)[0];
    if (line.trim().endsWith(':')) ind += '    ';
    e.preventDefault();
    t.setRangeText('\n' + ind, pos, pos, 'end');
    return true;
  }
  const PAIRS = { '(': ')', '[': ']', '{': '}', '"': '"', "'": "'" };
  const CLOSERS = new Set(Object.values(PAIRS));
  function handleBackspace(t, e) {
    if (t.selectionStart !== t.selectionEnd) return false;
    const v = t.value, pos = t.selectionStart;
    if (pos === 0) return false;
    // 빈 괄호/따옴표 쌍 사이 → 양쪽을 한 번에 지움
    if (PAIRS[v[pos - 1]] && PAIRS[v[pos - 1]] === v[pos]) { e.preventDefault(); t.setRangeText('', pos - 1, pos + 1, 'end'); return true; }
    // 줄 앞 공백이 4의 배수 → 들여쓰기 한 단계 지움
    const before = v.slice(v.lastIndexOf('\n', pos - 1) + 1, pos);
    if (before.length && /^ +$/.test(before) && before.length % 4 === 0) { e.preventDefault(); t.setRangeText('', pos - 4, pos, 'end'); return true; }
    return false;
  }
  function deleteWordBackward(t) {
    if (t.selectionStart !== t.selectionEnd) { t.setRangeText('', t.selectionStart, t.selectionEnd, 'end'); return; }
    const v = t.value, pos = t.selectionStart;
    let i = pos;
    while (i > 0 && (v[i - 1] === ' ' || v[i - 1] === '\t')) i--;
    if (i > 0 && v[i - 1] === '\n') i--;
    else if (i > 0 && /\w/.test(v[i - 1])) while (i > 0 && /\w/.test(v[i - 1])) i--;
    else while (i > 0 && !/[\w\s]/.test(v[i - 1])) i--;
    t.setRangeText('', i, pos, 'end');
  }
  // 괄호/따옴표 자동 닫기(선택 중이면 감싸기), 바로 뒤에 같은 닫는 문자가 있으면 지나가기
  function handleAutoPair(t, e) {
    if (e.isComposing) return false;
    const k = e.key, v = t.value, s = t.selectionStart, end = t.selectionEnd;
    if (PAIRS[k]) {
      e.preventDefault();
      if (s !== end) {
        const sel = v.slice(s, end);
        t.setRangeText(k + sel + PAIRS[k], s, end, 'end');
        t.selectionStart = s + 1; t.selectionEnd = s + 1 + sel.length;
      } else if ((k === '"' || k === "'") && (v[s] === k || /\w/.test(v[s - 1] || ''))) {
        // 닫는 따옴표 앞이면 지나가고, 단어 바로 뒤(예: don't)면 하나만 넣는다
        if (v[s] === k) t.selectionStart = t.selectionEnd = s + 1;
        else t.setRangeText(k, s, end, 'end');
      } else {
        t.setRangeText(k + PAIRS[k], s, end, 'end');
        t.selectionStart = t.selectionEnd = s + 1;
      }
      return true;
    }
    if (CLOSERS.has(k) && s === end && v[s] === k) { e.preventDefault(); t.selectionStart = t.selectionEnd = s + 1; return true; }
    return false;
  }

  /* =========================================================
     자동완성 — 키워드·내장함수·예외 이름 + 지금 코드에 나온 이름 + 객체.속성
     ========================================================= */
  const AC_KEYWORDS = ['False', 'None', 'True', 'and', 'as', 'assert', 'async', 'await', 'break', 'class', 'continue',
    'def', 'del', 'elif', 'else', 'except', 'finally', 'for', 'from', 'global', 'if', 'import', 'in', 'is', 'lambda',
    'nonlocal', 'not', 'or', 'pass', 'raise', 'return', 'try', 'while', 'with', 'yield', 'self', 'cls', 'match', 'case'];
  const AC_BUILTINS = ['print', 'len', 'range', 'str', 'int', 'float', 'bool', 'list', 'dict', 'set', 'tuple', 'frozenset',
    'bytes', 'bytearray', 'object', 'type', 'isinstance', 'issubclass', 'super', 'property', 'staticmethod', 'classmethod',
    'abstractmethod', 'open', 'input', 'enumerate', 'zip', 'map', 'filter', 'sorted', 'reversed', 'sum', 'min', 'max', 'abs',
    'round', 'pow', 'divmod', 'hash', 'id', 'repr', 'format', 'vars', 'dir', 'getattr', 'setattr', 'hasattr', 'delattr',
    'iter', 'next', 'all', 'any', 'callable', 'globals', 'locals', 'Optional', 'List', 'Dict', 'Tuple', 'Union', 'Any',
    'Callable', 'ABC', 'dataclass', 'field', 'Protocol', 'runtime_checkable', 'annotations', 'Path', 'json', 'tempfile',
    'dataclasses', 'typing', 'abc', 'pathlib', 'datetime', 'date', 'timedelta', 'math', 'random'];
  const AC_EXCEPTIONS = ['Exception', 'BaseException', 'ValueError', 'TypeError', 'KeyError', 'IndexError',
    'AttributeError', 'NotImplementedError', 'RuntimeError', 'StopIteration', 'PermissionError', 'FileNotFoundError',
    'FileExistsError', 'ZeroDivisionError', 'OverflowError', 'RecursionError', 'ImportError', 'ModuleNotFoundError',
    'NameError', 'UnboundLocalError', 'IndentationError', 'SyntaxError', 'OSError', 'ArithmeticError', 'AssertionError',
    'EOFError', 'LookupError', 'MemoryError', 'ConnectionError', 'TimeoutError', 'Warning', 'UserWarning',
    'DeprecationWarning', 'PendingDeprecationWarning'];
  // 점(.) 뒤에서 자주 쓰는 메서드
  const AC_METHODS = ['append', 'extend', 'insert', 'remove', 'pop', 'clear', 'index', 'count', 'sort', 'reverse', 'copy',
    'keys', 'values', 'items', 'get', 'update', 'setdefault', 'add', 'discard', 'join', 'split', 'strip', 'lstrip', 'rstrip',
    'replace', 'find', 'startswith', 'endswith', 'lower', 'upper', 'title', 'format', 'encode', 'decode', 'isdigit',
    'read_text', 'write_text', 'exists', 'name', 'dumps', 'loads', 'dump', 'load', '__init__', '__name__', '__class__'];
  const ac = { items: [], index: -1, start: 0 };

  function hideAutocomplete() { el.ac.classList.remove('show'); ac.items = []; ac.index = -1; }

  // 지금 코드에 나온 이름, '객체.xxx'로 쓰인 속성 이름, def 이름을 모은다.
  function docWords(text) {
    const words = new Set(), attrs = new Set();
    let m;
    const re = /[A-Za-z_][A-Za-z0-9_]*/g;
    while ((m = re.exec(text))) words.add(m[0]);
    const reAttr = /\.([A-Za-z_][A-Za-z0-9_]*)/g;
    while ((m = reAttr.exec(text))) attrs.add(m[1]);
    const reDef = /\bdef\s+([A-Za-z_]\w*)/g;
    while ((m = reDef.exec(text))) attrs.add(m[1]);
    return { words, attrs };
  }

  function updateAutocomplete(force) {
    const t = el.ta, v = t.value, pos = t.selectionStart;
    if (t.selectionStart !== t.selectionEnd) { hideAutocomplete(); return; }
    let start = pos;
    while (start > 0 && /[A-Za-z0-9_]/.test(v[start - 1])) start--;
    const word = v.slice(start, pos);
    const afterDot = v[start - 1] === '.';
    // 주석·문자열 안에서는 띄우지 않는다(간단 판정: 같은 줄에서 # 뒤이거나 따옴표 수가 홀수).
    const lineBefore = v.slice(v.lastIndexOf('\n', pos - 1) + 1, start);
    if (/#/.test(lineBefore.replace(/(["']).*?\1/g, '')) || (lineBefore.match(/["']/g) || []).length % 2) { hideAutocomplete(); return; }
    if (!word && !(force || afterDot)) { hideAutocomplete(); return; }
    if (/^\d/.test(word)) { hideAutocomplete(); return; }
    const { words, attrs } = docWords(v.slice(0, start) + v.slice(pos));
    const pool = afterDot ? new Set([...attrs, ...AC_METHODS])
      : new Set([...AC_KEYWORDS, ...AC_BUILTINS, ...AC_EXCEPTIONS, ...words]);
    const kindOf = (w) => afterDot ? (attrs.has(w) ? '속성' : '메서드')
      : AC_KEYWORDS.includes(w) ? '키워드' : AC_EXCEPTIONS.includes(w) ? '예외' : AC_BUILTINS.includes(w) ? '내장' : '코드';
    const lower = word.toLowerCase();
    const matches = [...pool].filter((w) => w !== word && w.toLowerCase().startsWith(lower))
      .sort((a, b) => (b.startsWith(word) - a.startsWith(word)) || a.length - b.length || a.localeCompare(b))
      .slice(0, 10);
    if (!matches.length) { hideAutocomplete(); return; }
    ac.items = matches; ac.index = 0; ac.start = start;
    el.ac.innerHTML = matches.map((w, i) =>
      '<div class="pr-ac-item' + (i === 0 ? ' active' : '') + '" data-i="' + i + '"><span><b>' + escapeHtml(w.slice(0, word.length)) +
      '</b>' + escapeHtml(w.slice(word.length)) + '</span><span class="pr-ac-kind">' + kindOf(w) + '</span></div>').join('');
    el.ac.querySelectorAll('.pr-ac-item').forEach((item) => item.addEventListener('mousedown', (e) => {
      e.preventDefault();
      ac.index = Number(item.dataset.i);
      acceptAutocomplete();
    }));
    el.ac.style.fontSize = fontSize + 'px';
    positionAutocomplete(start);
    el.ac.classList.add('show');
  }

  function positionAutocomplete(wordStart) {
    const t = el.ta, r = t.getBoundingClientRect(), lh = lineHeight();
    const before = t.value.slice(0, wordStart);
    const idx = before.split('\n').length - 1;
    const col = wordStart - before.lastIndexOf('\n') - 1;
    const x = r.left + 12 + col * charWidth() - t.scrollLeft;
    const y = r.top + 10 + (idx + 1) * lh - t.scrollTop;
    el.ac.style.left = Math.round(x) + 'px';
    el.ac.style.top = Math.round(y) + 'px';
    requestAnimationFrame(() => {
      const b = el.ac.getBoundingClientRect();
      if (b.right > innerWidth) el.ac.style.left = Math.max(4, innerWidth - b.width - 8) + 'px';
      if (b.bottom > innerHeight) el.ac.style.top = Math.max(4, y - b.height - lh) + 'px';
    });
  }

  function moveAutocomplete(dir) {
    ac.index = (ac.index + dir + ac.items.length) % ac.items.length;
    el.ac.querySelectorAll('.pr-ac-item').forEach((item, i) => item.classList.toggle('active', i === ac.index));
    const active = el.ac.querySelector('.active');
    if (active) active.scrollIntoView({ block: 'nearest' });
  }

  function acceptAutocomplete() {
    const word = ac.items[ac.index];
    if (word) el.ta.setRangeText(word, ac.start, el.ta.selectionStart, 'end');
    hideAutocomplete();
    afterEdit();
  }

  /* =========================================================
     키 입력
     ========================================================= */
  function onEditorKey(e) {
    const t = el.ta, cmd = e.ctrlKey || e.metaKey, k = e.key, lk = k.toLowerCase();
    if (el.ac.classList.contains('show')) {
      // 수식키 없이 누른 키만 목록이 가져간다(Alt+↓ 줄 이동, Shift+Tab 내어쓰기 등은 그대로 동작).
      const plain = !cmd && !e.altKey && !e.shiftKey;
      if (plain && k === 'ArrowDown') { e.preventDefault(); moveAutocomplete(1); return; }
      if (plain && k === 'ArrowUp') { e.preventDefault(); moveAutocomplete(-1); return; }
      if (plain && (k === 'Enter' || k === 'Tab')) { e.preventDefault(); acceptAutocomplete(); return; }
      if (k === 'Escape') { e.preventDefault(); hideAutocomplete(); return; }
      if (!plain || k === ' ' || /^(ArrowLeft|ArrowRight|Home|End|PageUp|PageDown)$/.test(k) ||
          (k.length === 1 && !/[A-Za-z0-9_]/.test(k))) hideAutocomplete();
    }
    let edited = true;
    if ((cmd && e.shiftKey && k === 'Enter') || k === 'F8') { e.preventDefault(); runMypy(); return; }
    if (cmd && e.shiftKey && lk === 'i') { e.preventDefault(); fixImports(); return; }
    if ((cmd && k === 'Enter') || k === 'F5') { e.preventDefault(); run(); return; }
    if (k === 'Escape') { e.preventDefault(); toggle(false); return; }
    if (cmd && k === ' ') { e.preventDefault(); updateAutocomplete(true); return; }
    if (cmd && !e.shiftKey && lk === 's') { e.preventDefault(); saveFile(); return; }
    if (cmd && lk === 'o') { e.preventDefault(); openFile(); return; }
    if (cmd && (k === '=' || k === '+')) { e.preventDefault(); applyFontSize(fontSize + 1); return; }
    if (cmd && k === '-') { e.preventDefault(); applyFontSize(fontSize - 1); return; }
    if (cmd && e.shiftKey && lk === 'k') { e.preventDefault(); deleteLine(t); }
    else if (cmd && lk === 'k') { e.preventDefault(); clearOutput(); return; }
    else if (cmd && !e.shiftKey && lk === 'z') { e.preventDefault(); undo(); return; }
    else if (cmd && (lk === 'y' || (lk === 'z' && e.shiftKey))) { e.preventDefault(); redo(); return; }
    else if (cmd && e.shiftKey && (k === '\\' || k === '|')) { e.preventDefault(); jumpToBracket(t); updateCurrentLine(); return; }
    else if (cmd && k === '/') { e.preventDefault(); toggleComment(t); }
    else if (cmd && (k === ']' || k === '[')) { e.preventDefault(); indent(t, k === '['); }
    else if (cmd && !e.shiftKey && lk === 'd') { e.preventDefault(); duplicateLine(t); }
    else if (cmd && k === 'Backspace') { e.preventDefault(); deleteWordBackward(t); }
    else if (e.altKey && e.shiftKey && (k === 'ArrowUp' || k === 'ArrowDown')) { e.preventDefault(); copyLine(t, k === 'ArrowUp' ? -1 : 1); }
    else if (e.altKey && !e.shiftKey && (k === 'ArrowUp' || k === 'ArrowDown')) { e.preventDefault(); moveLine(t, k === 'ArrowUp' ? -1 : 1); }
    else if (!cmd && !e.altKey && k === 'Home') { e.preventDefault(); smartHome(t, e.shiftKey); updateCurrentLine(); return; }
    else if (k === 'Tab') { e.preventDefault(); indent(t, e.shiftKey); }
    else if (k === 'Enter') { edited = handleEnter(t, e); }
    else if (k === 'Backspace') { edited = handleBackspace(t, e); }
    else if (!cmd && !e.altKey) { edited = handleAutoPair(t, e); }
    else edited = false;
    if (edited) afterEdit();
  }

  /* =========================================================
     테마
     ========================================================= */
  function applyTheme(name) {
    [el.panel, el.ac].forEach((node) => {
      if (name && name !== 'auto') node.dataset.prTheme = name;
      else delete node.dataset.prTheme;
    });
  }

  /* =========================================================
     빠진 import 자동 추가
     ========================================================= */
  // 이름 → 그 이름을 가져오는 모듈. 'from 모듈 import 이름' 꼴로 넣는다.
  const FROM_IMPORTS = {
    abc: ['ABC', 'abstractmethod', 'ABCMeta'],
    dataclasses: ['dataclass', 'field', 'asdict', 'astuple'],
    typing: ['Protocol', 'runtime_checkable', 'Optional', 'Any', 'Callable', 'Iterable', 'Iterator', 'Sequence',
      'Mapping', 'Union', 'ClassVar', 'Final', 'TypeVar', 'Generic', 'Literal', 'NamedTuple', 'TypedDict', 'override', 'cast'],
    pathlib: ['Path'],
    datetime: ['date', 'datetime', 'timedelta'],
    enum: ['Enum', 'IntEnum'],
    collections: ['defaultdict', 'Counter', 'deque', 'OrderedDict'],
    functools: ['wraps', 'lru_cache', 'cached_property', 'total_ordering'],
  };
  // 'json.dumps'처럼 모듈 이름 뒤에 점이 오면 'import 모듈'을 넣는다.
  const MODULE_IMPORTS = ['json', 'tempfile', 'math', 'random', 'os', 'sys', 're', 'time', 'copy', 'itertools', 'functools', 'collections', 'datetime'];

  // 문자열·주석을 지운 코드(이름 찾기용). 줄 수는 그대로 둔다.
  function stripStringsAndComments(code) {
    return code
      .replace(/("""|''')[\s\S]*?\1/g, (m) => m.replace(/[^\n]/g, ' '))
      .replace(/(["'])(?:\\.|(?!\1)[^\\\n])*\1/g, '""')
      .replace(/#.*$/gm, '');
  }

  function missingImports(code) {
    const bare = stripStringsAndComments(code);
    const have = new Set();   // 이미 import 했거나 코드 안에서 직접 만든 이름
    let m;
    const reFrom = /^\s*from\s+[\w.]+\s+import\s+\(?([^)\n]+)/gm;
    while ((m = reFrom.exec(bare))) m[1].split(',').forEach((n) => { const w = n.trim().split(/\s+as\s+/).pop(); if (w) have.add(w); });
    const reImp = /^\s*import\s+([^\n]+)/gm;
    while ((m = reImp.exec(bare))) m[1].split(',').forEach((n) => { const w = n.trim().split(/\s+as\s+/).pop().split('.')[0]; if (w) have.add(w); });
    const reDef = /^\s*(?:class|def|async\s+def)\s+(\w+)/gm;
    while ((m = reDef.exec(bare))) have.add(m[1]);
    const reAssign = /^\s*(\w+)\s*(?::[^=\n]+)?=(?!=)/gm;
    while ((m = reAssign.exec(bare))) have.add(m[1]);
    const used = (name) => new RegExp('(^|[^\\w.])' + name + '\\b').test(bare);
    const from = {};
    Object.entries(FROM_IMPORTS).forEach(([mod, names]) => names.forEach((n) => {
      if (!have.has(n) && used(n) && !(mod === 'datetime' && n === 'datetime' && /(^|[^\w.])datetime\./.test(bare))) {
        (from[mod] = from[mod] || []).push(n);
      }
    }));
    const modules = MODULE_IMPORTS.filter((mod) => !have.has(mod) && new RegExp('(^|[^\\w.])' + mod + '\\.\\w').test(bare));
    return { from, modules };
  }

  function addMissingImports(code) {
    const { from, modules } = missingImports(code);
    const lines = modules.map((mod) => 'import ' + mod)
      .concat(Object.entries(from).map(([mod, names]) => 'from ' + mod + ' import ' + names.join(', ')));
    if (!lines.length) return code;
    // 모듈 설명(docstring)과 from __future__ 줄 다음, 기존 import 앞에 넣는다.
    const src = code.split('\n');
    let at = 0;
    const doc = code.match(/^\s*("""|''')[\s\S]*?\1[^\n]*\n/);
    if (doc) at = doc[0].split('\n').length - 1;
    while (at < src.length && /^\s*from\s+__future__\s+import/.test(src[at])) at++;
    const nextIsImport = /^\s*(import|from)\s/.test(src[at] || '');
    const block = lines.join('\n') + (nextIsImport ? '\n' : '\n\n\n');
    src.splice(at, 0, block.replace(/\n$/, ''));
    return src.join('\n');
  }

  function fixImports() {
    const before = el.ta.value;
    const after = addMissingImports(before);
    if (after === before) { setStatus('빠진 import 없음', 'ok'); return; }
    const added = after.split('\n').length - before.split('\n').length;
    histTrack();
    el.ta.value = after;
    afterEdit();
    histTrack();
    setStatus('import ' + Math.max(1, added - 2) + '줄 추가', 'ok');
  }

  /* =========================================================
     mypy 타입 검사 (최신 mypy를 브라우저 안에 설치해 돌린다)
     ========================================================= */
  function ensureMypy() {
    if (mypyPromise) return mypyPromise;
    mypyPromise = (async () => {
      const py = await loadPyodideOnce();
      await py.loadPackage('micropip', { messageCallback: () => {} });   // 'Loading ...' 안내는 출력 칸에 넣지 않는다
      await py.pyimport('micropip').install(MYPY_SPEC);
      return py;
    })();
    mypyPromise.catch(() => { mypyPromise = null; });
    return mypyPromise;
  }

  async function runMypy() {
    if (running) return;
    running = true;
    el.run.disabled = true;
    $('.pr-mypy').disabled = true;
    hideAutocomplete();
    clearOutput();
    errorLines.clear();
    refresh();
    try {
      setStatus(mypyPromise ? 'mypy 검사 중…' : 'mypy 설치 중… (처음 한 번만, 20초 정도)', 'loading');
      await new Promise((r) => setTimeout(r, 30));   // 상태 글자가 먼저 그려지도록
      const py = await ensureMypy();
      el.out.textContent = '';   // 설치 중 출력된 안내 지우기
      setStatus('mypy 검사 중…', 'loading');
      await new Promise((r) => setTimeout(r, 30));
      py.FS.mkdirTree('/tmp/pyrunner');
      py.FS.writeFile('/tmp/pyrunner/code.py', el.ta.value);
      const t0 = performance.now();
      // 수업 기준(Python 3.12)에 맞춰 검사한다. 캐시를 남겨 두 번째부터는 빠르다.
      const result = py.runPython(
        "from mypy import api as _mypy_api\n" +
        "_r = _mypy_api.run(['/tmp/pyrunner/code.py', '--python-version', '3.12', '--show-column-numbers',\n" +
        "                    '--no-color-output', '--cache-dir', '/tmp/pyrunner/.mypy_cache'])\n" +
        "_r[0] + _r[1]");
      showMypy(String(result), performance.now() - t0);
    } catch (err) {
      append('mypy를 실행하지 못했습니다.\n' + String(err && err.message ? err.message : err) + '\n', 'pr-err');
      setStatus('mypy 오류', 'err');
    } finally {
      running = false;
      el.run.disabled = false;
      $('.pr-mypy').disabled = false;
    }
  }

  // '/tmp/pyrunner/code.py:6:19: error: ...' → '6:19 error: ...' (줄 번호는 눌러서 이동)
  function showMypy(text, ms) {
    let errors = 0, notes = 0;
    text.replace(/\n$/, '').split('\n').forEach((line) => {
      const m = line.match(/^\/tmp\/pyrunner\/code\.py:(\d+):(?:(\d+):)?\s*(error|note|warning):\s*(.*)$/);
      if (!m) {
        if (/^Success:/.test(line)) append('✓ ' + line + '\n', 'pr-ok');
        else if (line.trim()) append(line + '\n', /^Found \d+ error/.test(line) ? 'pr-err' : 'pr-muted');
        return;
      }
      const [, ln, col, kind, msg] = m;
      if (kind === 'error') { errors++; errorLines.add(Number(ln)); } else notes++;
      const span = document.createElement('span');
      span.className = kind === 'error' ? 'pr-err' : 'pr-muted';
      const a = document.createElement('a');
      a.className = 'pr-jump';
      a.dataset.line = ln;
      a.textContent = ln + (col ? ':' + col : '');
      a.title = ln + '번째 줄로 이동';
      span.append(a, ' ' + kind + ': ' + msg + '\n');
      el.out.appendChild(span);
    });
    refresh();
    setStatus(errors ? 'mypy: 오류 ' + errors + '개' : 'mypy: 문제 없음 (' + ms.toFixed(0) + 'ms)', errors ? 'err' : 'ok');
  }

  /* =========================================================
     실행
     ========================================================= */
  function setStatus(msg, kind) { el.status.textContent = msg || ''; el.status.dataset.kind = kind || ''; }
  function append(text, cls) {
    if (!text) return;
    const span = document.createElement('span');
    if (cls) span.className = cls;
    span.textContent = text;
    el.out.appendChild(span);
    el.out.scrollTop = el.out.scrollHeight;
  }
  function clearOutput() { el.out.textContent = ''; setStatus(''); }
  // input()의 안내문은 줄바꿈 없이 출력되므로, 출력의 마지막 줄을 입력창 안내문으로 쓴다.
  function lastOutputLine() { const s = el.out.textContent; return s.slice(s.lastIndexOf('\n') + 1); }

  function goToLine(n) {
    const lines = el.ta.value.split('\n');
    if (n < 1 || n > lines.length) return;
    const pos = lines.slice(0, n - 1).reduce((a, l) => a + l.length + 1, 0);
    el.ta.focus();
    el.ta.setSelectionRange(pos, pos + lines[n - 1].length);
    scrollCaretIntoView();
    syncScroll();
  }

  async function run() {
    if (running) return;
    running = true;
    el.run.disabled = true;
    hideAutocomplete();
    clearOutput();
    errorLines.clear();
    refresh();
    let ns = null;
    try {
      setStatus('Python 불러오는 중… (처음 한 번만)', 'loading');
      const py = await loadPyodideOnce();
      setStatus('실행 중…', 'loading');
      const dec = new TextDecoder(), decErr = new TextDecoder();
      py.setStdout({ write: (buf) => { append(dec.decode(buf, { stream: true })); return buf.length; } });
      py.setStderr({ write: (buf) => { append(decErr.decode(buf, { stream: true }), 'pr-err'); return buf.length; } });
      py.setStdin({
        stdin: () => {
          const answer = window.prompt(lastOutputLine() || 'input() 값을 입력하세요', '');
          if (answer === null) return null;           // 취소 → EOFError
          append(answer + '\n', 'pr-input');
          return answer;
        },
      });
      // 실행할 때마다 새 이름공간: 이전 실행의 변수·클래스가 섞이지 않는다.
      ns = py.globals.get('dict')();
      ns.set('__name__', '__main__');
      const t0 = performance.now();
      await py.runPythonAsync(el.ta.value, { globals: ns, filename: '<code>' });
      if (!el.out.textContent) append('(출력 없음)\n', 'pr-muted');
      setStatus('완료 (' + (performance.now() - t0).toFixed(0) + 'ms)', 'ok');
    } catch (err) {
      showError(String(err && err.message ? err.message : err));
      setStatus('오류', 'err');
    } finally {
      if (ns) ns.destroy();
      running = false;
      el.run.disabled = false;
    }
  }

  // 트레이스백에서 Pyodide 내부 줄은 빼고, 내 코드의 줄 번호는 눌러서 이동할 수 있게 만든다.
  function showError(msg) {
    const keep = [];
    let skipping = false;
    msg.replace(/\n$/, '').split('\n').forEach((l) => {
      if (/^\s*File "\/lib\/python/.test(l)) { skipping = true; return; }
      if (skipping && /^\s{4}/.test(l)) return;
      skipping = false;
      keep.push(l);
    });
    let last = 0;
    keep.forEach((l) => {
      const m = l.match(/File "<code>", line (\d+)/);
      if (!m) { append(l + '\n', 'pr-err'); return; }
      last = Number(m[1]);
      const span = document.createElement('span');
      span.className = 'pr-err';
      const a = document.createElement('a');
      a.className = 'pr-jump';
      a.dataset.line = m[1];
      a.textContent = m[0];
      a.title = m[1] + '번째 줄로 이동';
      span.append(l.slice(0, m.index), a, l.slice(m.index + m[0].length) + '\n');
      el.out.appendChild(span);
    });
    if (last) {
      errorLines.add(last);
      refresh();
      const btn = document.createElement('a');
      btn.className = 'pr-jump pr-jumpbtn';
      btn.dataset.line = String(last);
      btn.textContent = '→ ' + last + '번째 줄로 이동';
      el.out.appendChild(btn);
    }
    el.out.scrollTop = el.out.scrollHeight;
  }

  /* =========================================================
     파일 저장·불러오기·초기화·출력 복사
     ========================================================= */
  function saveFile() {
    const base = (document.title || 'code').replace(/[\\/:*?"<>|]/g, '').trim().replace(/\s+/g, '_') || 'code';
    const a = document.createElement('a');
    a.href = URL.createObjectURL(new Blob([el.ta.value], { type: 'text/x-python' }));
    a.download = base + '.py';
    document.body.appendChild(a);
    a.click();
    setTimeout(() => { URL.revokeObjectURL(a.href); a.remove(); }, 0);
    setStatus(a.download + ' 저장', 'ok');
  }
  function openFile() {
    const input = document.createElement('input');
    input.type = 'file';
    input.accept = '.py,text/x-python,text/plain';
    input.onchange = () => {
      const file = input.files[0];
      if (!file) return;
      file.text().then((text) => { setCode(text); setStatus(file.name + ' 불러옴', 'ok'); el.ta.focus(); });
    };
    input.click();
  }
  function resetEditor() {
    if (!window.confirm('편집기 내용을 모두 지웁니다. 계속할까요? (Ctrl+Z로 되돌릴 수 있어요)')) return;
    setCode('');
    clearOutput();
    el.ta.focus();
  }
  function copyOutput() {
    const text = el.out.textContent;
    const done = () => setStatus('출력 복사됨', 'ok');
    const fallback = () => {
      const tmp = document.createElement('textarea');
      tmp.value = text;
      document.body.appendChild(tmp);
      tmp.select();
      document.execCommand('copy');
      tmp.remove();
      done();
    };
    if (navigator.clipboard && window.isSecureContext) navigator.clipboard.writeText(text).then(done, fallback);
    else fallback();
  }

  /* =========================================================
     Alt+P로 열고 닫기
     ========================================================= */
  // 한글 입력 상태(ㅔ)·맥 Option(π)에서도 P 자리 키로 인식하도록 code·key·keyCode를 모두 본다.
  // 페이지의 다른 스크립트가 이벤트를 막아도 먼저 받도록 캡처 단계에서 듣는다.
  function isAltP(e) {
    if (!e.altKey || e.ctrlKey || e.metaKey || e.shiftKey) return false;
    return e.code === 'KeyP' || e.keyCode === 80 || /^[pPㅔπ]$/.test(e.key);
  }
  window.addEventListener('keydown', (e) => {
    if (!isAltP(e) || e.repeat || !el.panel) return;
    e.preventDefault();
    e.stopPropagation();
    toggle();
  }, true);
  window.addEventListener('resize', () => { if (el.panel && isOpen()) refresh(); });

  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', build);
  else build();
})();
