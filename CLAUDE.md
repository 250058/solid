# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## 하네스: 파이썬 SOLID 수업자료 제작

**목표:** 파이썬 기반 SOLID 원칙 수업자료(개념+상황+주석 코드+박스 설명란+이해 점검) 제작

**트리거:** SOLID/객체지향 수업자료 제작·수정·재실행 요청 시 `solid-lesson-orchestrator` 스킬을 사용하라. 단순 질문은 직접 응답 가능.

**변경 이력:**
| 날짜 | 변경 내용 | 대상 | 사유 |
|------|----------|------|------|
| 2026-10-09 | 초기 구성 | 전체 | - |
| 2026-10-09 | 산출물 형식 Markdown → HTML | skills 3종, agents 3종 | 사용자 요청(html 파일로 제작) |
| 2026-10-09 | 퀴즈 유형 '개념 적용' 추가 | skills/solid-quiz-design | 첫 실행 QA에서 표에 없는 유형 사용 발견 |
| 2026-10-21 | 산출물을 개념기반탐구학습지(3차시) + 교사 가이드 + 별도 정답 파일로 전환. 기존 7장 교재는 사전 읽기 자료로 보존 | skills/solid-lesson-orchestrator(개정), skills/solid-inquiry-worksheet·solid-teacher-guide(신규), agents/worksheet-writer·teacher-guide-writer(신규), curriculum-designer·qa-reviewer·quiz-designer(수정) | 사용자 요청(개념기반탐구학습지, 학생 활동 극대화, 3차시, 교사 가이드·정답 분리) |
| 2026-10-21 | 학습지 시작 코드 점검은 '구체 타입 힌트로 우회'하는 오답을 잡는지 검증, 정의 박스는 일반화 후 열람(details)으로 규칙화 | skills/solid-inquiry-worksheet | 첫 실행 QA에서 점검 구멍·정의 선공개 발견 |
| 2026-10-21 | 학습지 입력 JSON 저장/불러오기(학습지당 파일 하나, 고정 파일명) 추가, 교사용 학생 제출 뷰어(student_viewer) 추가 | assets/worksheet.js, skills/solid-teacher-guide(scripts·assets 추가) | 사용자 요청(학생 데이터 JSON 저장·불러오기, 교사가 학생 파일 불러오기) |
| 2026-10-22 | 학습지 입력칸 전체(1~3차시)의 예시 정답 JSON 추가(학습지 `📂 JSON 불러오기`로 불러올 수 있는 형식, 교사용·비공개) | teacher/sample_answers/session_N_예시정답.json | 사용자 요청(교사 참조용 예시 정답, 학습지에서 불러오기) |
| 2026-10-22 | 시작 코드 내려받기 링크(개별 파일 + 배포 시 생성되는 zip)와 실행 안내 수정, 학습지 머리말에 링크 추가 | index.html, worksheets/session_1~3.html, .github/workflows/pages.yml | 사용자 요청(학생에게 solid_course 폴더가 제공되지 않음) |
| 2026-10-23 | 대상 Python 버전 3.10+ → 3.12+ 로 표기 통일(index, 학습지 머리말, 시작 코드 docstring, 교사 가이드·정답 파일, skills 3종). 3.12·3.13에서 시작 코드·정답 코드·교재 코드 전부 실행 확인 | index.html, worksheets/*, teacher/*, skills/solid-lesson-writing·solid-inquiry-worksheet·solid-teacher-guide | 사용자 요청(Python 3.12 이상 기준) |
