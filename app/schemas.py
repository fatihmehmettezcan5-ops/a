from typing import Literal

from pydantic import BaseModel, Field


CoachMode = Literal["auto", "ai", "rule"]
MoveCategory = Literal[
    "brilliant",
    "great",
    "good",
    "inaccuracy",
    "mistake",
    "blunder",
]


class ReviewRequest(BaseModel):
    pgn: str = Field(..., description="Single game PGN text")
    stockfish_path: str = Field("stockfish", description="UCI engine binary path")
    depth: int = Field(14, ge=8, le=30)
    time_limit: float = Field(0.08, ge=0.01, le=2.0)
    coach_mode: CoachMode = "auto"


class ReviewedMove(BaseModel):
    ply: int
    side: Literal["white", "black"]
    san: str
    uci: str
    category: MoveCategory
    centipawn_loss: int
    eval_before_cp: int
    eval_after_cp: int
    best_move_uci: str
    comment: str
    coach_comment: str | None = None


class ReviewSummary(BaseModel):
    brilliant: int = 0
    great: int = 0
    good: int = 0
    inaccuracy: int = 0
    mistake: int = 0
    blunder: int = 0


class ReviewResponse(BaseModel):
    summary: ReviewSummary
    moves: list[ReviewedMove]
