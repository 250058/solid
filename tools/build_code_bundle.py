"""Python 실행창의 '코드 가져오기' 목록에 들어갈 코드 묶음(code_bundle.js)을 만든다.

아래 폴더의 .py 파일을 모두 읽어 solid_course/assets/code_bundle.js 한 파일로 묶는다.
학습지·교재 페이지는 file:// 로 열어도 동작해야 하는데, 브라우저는 file:// 에서 다른 파일을
fetch로 읽지 못하게 막으므로 코드를 미리 JS 파일 안에 넣어 둔다.

코드 파일을 추가·수정한 뒤 다시 실행하면 목록이 갱신된다(GitHub Pages 배포 때도 자동 실행).

실행 방법
    python tools/build_code_bundle.py
"""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent / "solid_course"
# (목록에 보일 묶음 이름, 폴더) — 새 폴더를 목록에 넣으려면 여기에 한 줄 추가한다.
GROUPS = [
    ("학습지 시작 코드", ROOT / "worksheets" / "code"),
    ("교재 예제 코드", ROOT / "code"),
]
OUT = ROOT / "assets" / "code_bundle.js"


def first_doc_line(code: str) -> str:
    """모듈 설명(docstring)의 첫 줄. 없으면 빈 문자열."""
    text = code.lstrip()
    for quote in ('"""', "'''"):
        if text.startswith(quote):
            # 여는 따옴표 다음 줄부터 설명이 시작하는 경우도 있다.
            doc = text[3:].split(quote, 1)[0]
            return next((line.strip() for line in doc.splitlines() if line.strip()), "")
    return ""


def main() -> None:
    files = []
    for group, folder in GROUPS:
        for path in sorted(folder.glob("*.py")):
            code = path.read_text(encoding="utf-8")
            files.append({
                "group": group,
                "name": path.name,
                "path": path.relative_to(ROOT).as_posix(),
                "title": first_doc_line(code),
                "code": code,
            })
    body = json.dumps(files, ensure_ascii=False, indent=1)
    OUT.write_text(
        "/* 자동 생성 파일 — 직접 고치지 말고 tools/build_code_bundle.py 를 다시 실행하세요. */\n"
        f"window.PYRUNNER_FILES = {body};\n",
        encoding="utf-8",
    )
    print(f"{OUT.relative_to(ROOT.parent)}: 파일 {len(files)}개")


if __name__ == "__main__":
    main()
