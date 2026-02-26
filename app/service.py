from io import StringIO

import chess
import chess.engine
import chess.pgn

from app.coach import get_coach_comment
from app.schemas import ReviewRequest, ReviewResponse, ReviewedMove, ReviewSummary


def _score_cp(score: chess.engine.PovScore, pov: chess.Color) -> int:
    return score.pov(pov).score(mate_score=100000)


def _classify_move(cp_loss: int, is_best: bool, best_gap: int) -> str:
    if cp_loss >= 250:
        return "blunder"
    if cp_loss >= 120:
        return "mistake"
    if cp_loss >= 60:
        return "inaccuracy"
    if is_best and best_gap >= 150:
        return "brilliant"
    if is_best and best_gap >= 70:
        return "great"
    return "good"


def _comment_for(category: str, cp_loss: int, best_move_uci: str) -> str:
    if category == "blunder":
        return f"Ciddi hata: yaklaşık {cp_loss} cp kayıp. En güçlü fikir: {best_move_uci}."
    if category == "mistake":
        return f"Daha iyi devam yolu kaçtı ({cp_loss} cp). Önerilen hamle: {best_move_uci}."
    if category == "inaccuracy":
        return f"Küçük bir isabetsizlik ({cp_loss} cp). Daha iyi alternatif: {best_move_uci}."
    if category == "brilliant":
        return "Mükemmel zamanlama ve yüksek doğrulukta hamle."
    if category == "great":
        return "Çok güçlü hamle; pozisyonun taleplerine iyi cevap veriyor."
    return "Doğal ve oynanabilir bir hamle."


def review_game(req: ReviewRequest) -> ReviewResponse:
    game = chess.pgn.read_game(StringIO(req.pgn))
    if game is None:
        raise ValueError("PGN parse edilemedi")

    summary = ReviewSummary()
    reviewed: list[ReviewedMove] = []

    engine = chess.engine.SimpleEngine.popen_uci(req.stockfish_path)
    board = game.board()
    try:
        for ply, move in enumerate(game.mainline_moves(), start=1):
            mover = board.turn
            side = "white" if mover == chess.WHITE else "black"
            san = board.san(move)

            info_multi = engine.analyse(
                board,
                chess.engine.Limit(depth=req.depth, time=req.time_limit),
                multipv=2,
            )
            best_info = info_multi[0]
            second_info = info_multi[1] if len(info_multi) > 1 else info_multi[0]

            best_move = best_info["pv"][0]
            best_move_uci = best_move.uci()
            eval_before = _score_cp(best_info["score"], mover)
            best_gap = _score_cp(best_info["score"], mover) - _score_cp(second_info["score"], mover)

            board.push(move)
            info_after = engine.analyse(
                board,
                chess.engine.Limit(depth=req.depth, time=req.time_limit),
            )
            eval_after = _score_cp(info_after["score"], mover)

            cp_loss = max(0, eval_before - eval_after)
            is_best = move == best_move
            category = _classify_move(cp_loss, is_best, best_gap)

            setattr(summary, category, getattr(summary, category) + 1)
            comment = _comment_for(category, cp_loss, best_move_uci)
            coach_comment = get_coach_comment(
                req.coach_mode,
                category,
                san,
                cp_loss,
                eval_before,
                eval_after,
            )

            reviewed.append(
                ReviewedMove(
                    ply=ply,
                    side=side,
                    san=san,
                    uci=move.uci(),
                    category=category,
                    centipawn_loss=cp_loss,
                    eval_before_cp=eval_before,
                    eval_after_cp=eval_after,
                    best_move_uci=best_move_uci,
                    comment=comment,
                    coach_comment=coach_comment,
                )
            )
    finally:
        engine.quit()

    return ReviewResponse(summary=summary, moves=reviewed)
