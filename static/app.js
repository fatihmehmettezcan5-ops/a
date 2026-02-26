const form = document.getElementById("review-form");
const statusEl = document.getElementById("status");
const summaryEl = document.getElementById("summary");
const movesEl = document.getElementById("moves");

function renderSummary(summary) {
  summaryEl.innerHTML = `
    <h2>Özet</h2>
    <ul>
      <li>Brilliant: ${summary.brilliant}</li>
      <li>Great: ${summary.great}</li>
      <li>Good: ${summary.good}</li>
      <li>Inaccuracy: ${summary.inaccuracy}</li>
      <li>Mistake: ${summary.mistake}</li>
      <li>Blunder: ${summary.blunder}</li>
    </ul>
  `;
}

function renderMoves(moves) {
  movesEl.innerHTML = `<h2>Hamleler</h2>`;
  moves.forEach((move) => {
    const coach = move.coach_comment ? `<p><strong>Koç:</strong> ${move.coach_comment}</p>` : "";
    const card = document.createElement("article");
    card.className = "move-card";
    card.innerHTML = `
      <span class="badge ${move.category}">${move.category.toUpperCase()}</span>
      <p><strong>#${move.ply} ${move.side}</strong> — ${move.san} (${move.uci})</p>
      <p>Eval: ${move.eval_before_cp} → ${move.eval_after_cp} | Kayıp: ${move.centipawn_loss} cp</p>
      <p><strong>En iyi hamle:</strong> ${move.best_move_uci}</p>
      <p>${move.comment}</p>
      ${coach}
    `;
    movesEl.appendChild(card);
  });
}

form.addEventListener("submit", async (e) => {
  e.preventDefault();
  statusEl.textContent = "Analiz yapılıyor...";
  statusEl.className = "";
  summaryEl.innerHTML = "";
  movesEl.innerHTML = "";

  const payload = {
    pgn: document.getElementById("pgn").value,
    stockfish_path: document.getElementById("stockfish_path").value,
    depth: Number(document.getElementById("depth").value),
    time_limit: Number(document.getElementById("time_limit").value),
    coach_mode: document.getElementById("coach_mode").value,
  };

  try {
    const res = await fetch("/review", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    if (!res.ok) {
      const text = await res.text();
      throw new Error(text || "Analiz başarısız");
    }

    const data = await res.json();
    statusEl.textContent = "Analiz tamamlandı.";
    renderSummary(data.summary);
    renderMoves(data.moves);
  } catch (error) {
    statusEl.textContent = `Hata: ${error.message}`;
    statusEl.className = "error";
  }
});
