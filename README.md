# Chess.com Benzeri Ücretsiz Oyun İncelemesi (Game Review)

Bu proje, bir PGN oyunu için **Chess.com Game Review benzeri** etiketler üretir ve web arayüzünde gösterir:

- Brilliant
- Great
- Good
- Inaccuracy
- Mistake
- Blunder

Ayrıca önemli hamleler için **AI destekli eğitmen görüşü** üretir.

## Özellikler

- Stockfish ile hamle değerlendirme
- Hamle kaybına göre sınıflandırma
- `multipv` ile en iyi hamle karşılaştırması
- AI koç görüşü (`OPENAI_API_KEY` varsa) + kural tabanlı fallback
- Basit web arayüzü (PGN yapıştır, analiz sonucu kartlar halinde gör)

## Kurulum

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Çalıştırma

```bash
uvicorn app.main:app --reload
```

Ardından tarayıcıda:
- `http://127.0.0.1:8000/` (web arayüz)
- `http://127.0.0.1:8000/docs` (Swagger)

## API

### `POST /review`

Örnek istek:

```json
{
  "pgn": "1. e4 e5 2. Nf3 Nc6 3. Bb5 a6 4. Ba4 Nf6 *",
  "stockfish_path": "stockfish",
  "depth": 14,
  "time_limit": 0.08,
  "coach_mode": "auto"
}
```

- `coach_mode` değerleri:
  - `auto`: API key varsa AI, yoksa fallback
  - `ai`: sadece AI (key yoksa hata)
  - `rule`: sadece kural tabanlı

## Notlar

- Chess.com sınıflandırma mantığı birebir public değil; burada benzer bir yaklaşım uygulanmıştır.
- Daha tıpatıp sonuç için analiz süresini/depth değerini artırabilirsiniz.
