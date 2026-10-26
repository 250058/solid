// 선택형(choice/ox): 보기를 클릭하면 정오 표시 + 해설 공개. open: 버튼으로 해설 토글.
document.addEventListener("DOMContentLoaded", () => {
  document.querySelectorAll("section.quiz").forEach(sec => {
    let total = 0, correct = 0;
    const score = document.createElement("div");
    score.className = "score";
    sec.querySelectorAll(".q").forEach(q => {
      const type = q.dataset.type, ex = q.querySelector(".explain");
      if (type === "open") {
        const b = document.createElement("button");
        b.className = "reveal"; b.textContent = "해설 보기";
        b.onclick = () => { ex.classList.toggle("show"); b.textContent = ex.classList.contains("show") ? "해설 닫기" : "해설 보기"; };
        q.insertBefore(b, ex);
        return;
      }
      total++;
      const ans = Number(q.dataset.answer);
      q.querySelectorAll(".options li").forEach((li, i) => {
        li.onclick = () => {
          if (q.classList.contains("done")) return;
          q.classList.add("done");
          const ok = i + 1 === ans;
          li.classList.add(ok ? "right" : "wrong");
          if (!ok) q.querySelectorAll(".options li")[ans - 1].classList.add("right");
          if (ok) correct++;
          ex.classList.add("show");
          score.textContent = `객관식/OX 점수: ${correct} / ${total}`;
        };
      });
    });
    if (total) sec.appendChild(score);
  });
});
