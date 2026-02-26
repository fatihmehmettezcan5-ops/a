import os

from openai import OpenAI


def rule_based_coach_comment(category: str, san: str, cp_loss: int) -> str:
    if category == "brilliant":
        return f"{san} çok güçlü bir hamle. Pozisyonun kritik anında en etkili yolu bulmuşsun."
    if category == "great":
        return f"{san} çok kaliteli bir tercih; rakibin kaynaklarını ciddi biçimde sınırlıyor."
    if category == "good":
        return f"{san} sağlam bir hamle. Planını koruyup konumu dengede tutuyor."
    if category == "inaccuracy":
        return f"{san} oynanabilir ama daha iyi bir seçenek vardı (yaklaşık {cp_loss} cp kayıp)."
    if category == "mistake":
        return f"{san} ile belirgin avantaj kaybı var ({cp_loss} cp). Benzer konumda tehditleri önce kontrol et."
    return f"{san} ciddi bir blunder ({cp_loss} cp). Hamle öncesi rakibin taktik cevaplarını tek tek elemek faydalı olur."


def ai_coach_comment(category: str, san: str, cp_loss: int, eval_before: int, eval_after: int) -> str:
    client = OpenAI(api_key=os.environ["OPENAI_API_KEY"])
    prompt = (
        "Sen satranç koçusun. Türkçe, kısa, uygulanabilir geri bildirim ver. "
        "Maksimum 2 cümle yaz. Teknik ama anlaşılır ol.\n"
        f"Kategori: {category}\n"
        f"Hamle: {san}\n"
        f"Kayıp (cp): {cp_loss}\n"
        f"Eval önce: {eval_before}, sonra: {eval_after}\n"
    )
    response = client.responses.create(
        model="gpt-4.1-mini",
        input=prompt,
        max_output_tokens=100,
    )
    return response.output_text.strip()


def get_coach_comment(
    coach_mode: str,
    category: str,
    san: str,
    cp_loss: int,
    eval_before: int,
    eval_after: int,
) -> str | None:
    if category not in {"brilliant", "mistake", "blunder"}:
        return None

    has_key = bool(os.getenv("OPENAI_API_KEY"))
    if coach_mode == "rule":
        return rule_based_coach_comment(category, san, cp_loss)

    if coach_mode == "ai":
        if not has_key:
            raise ValueError("coach_mode='ai' için OPENAI_API_KEY gerekli")
        return ai_coach_comment(category, san, cp_loss, eval_before, eval_after)

    if has_key:
        return ai_coach_comment(category, san, cp_loss, eval_before, eval_after)
    return rule_based_coach_comment(category, san, cp_loss)
