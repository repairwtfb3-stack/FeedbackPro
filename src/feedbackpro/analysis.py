from __future__ import annotations

import re

from .domain import ANALYSIS_VERSION, AnalysisResult, Criticality, Review, Sentiment

_TOKEN_RE = re.compile(r"[A-Za-zА-Яа-яЁё0-9-]+", re.UNICODE)
POSITIVE = {"отлично", "отличный", "хорошо", "хороший", "быстро", "удобно", "доволен", "довольна", "рекомендую", "спасибо", "качественный", "вежливый", "супер", "прекрасно", "понравилось", "идеально"}
NEGATIVE = {"плохо", "плохой", "ужасно", "ужасный", "медленно", "грубо", "сломался", "сломано", "брак", "просрочка", "задержка", "обман", "ошибка", "верните", "жалоба", "недоволен", "недовольна", "некачественный", "хамство"}
INTENSIFIERS = {"очень", "крайне", "совсем", "абсолютно", "дважды", "повторно"}
NEGATIONS = {"не", "нет", "никогда", "ни"}
ASPECT_RULES = {
    "quality": {"качество", "брак", "сломался", "сломано", "дефект", "товар"},
    "price": {"цена", "дорого", "дешево", "стоимость", "скидка"},
    "delivery": {"доставка", "курьер", "привезли", "задержка", "срок"},
    "service": {"сервис", "обслуживание", "менеджер", "консультант"},
    "staff": {"персонал", "сотрудник", "кассир", "хамство", "грубо"},
    "support": {"поддержка", "оператор", "чат", "звонок", "ответ"},
    "return": {"возврат", "верните", "гарантия", "обмен"},
    "digital": {"сайт", "приложение", "личный", "кабинет", "оплата"},
    "availability": {"наличие", "нет", "закончился", "склад"},
}
CRITICAL_MARKERS = {"деньги", "списали", "мошенничество", "опасно", "травма", "суд", "прокуратура", "роспотребнадзор", "утечка", "персональные", "данные"}
HIGH_MARKERS = {"обман", "повторно", "дважды", "жалоба", "брак", "верните"}


def _tokens(text: str) -> list[str]:
    return [x.casefold() for x in _TOKEN_RE.findall(text)]


class AnalysisPipeline:
    def analyze(self, review: Review) -> AnalysisResult:
        tokens = _tokens(review.normalized_text)
        score = 0.0
        hits: list[str] = []
        for i, token in enumerate(tokens):
            weight = 1.5 if i and tokens[i - 1] in INTENSIFIERS else 1.0
            negated = bool(i and tokens[i - 1] in NEGATIONS)
            if token in POSITIVE:
                score += -weight if negated else weight
                hits.append(("not " if negated else "") + token)
            elif token in NEGATIVE:
                score += weight if negated else -weight
                hits.append(("not " if negated else "") + token)
        if review.rating is not None:
            if review.rating <= 2:
                score -= 0.75
            elif review.rating >= 4:
                score += 0.75
        sentiment = Sentiment.POSITIVE if score > 0.35 else Sentiment.NEGATIVE if score < -0.35 else Sentiment.NEUTRAL
        confidence = min(0.98, 0.50 + 0.10 * abs(score) + 0.03 * len(hits))
        token_set = set(tokens)
        aspects = tuple([k for k, words in ASPECT_RULES.items() if token_set & words] or ["other"])
        risk = 2 if sentiment is Sentiment.NEGATIVE else 0
        critical_hits = len(token_set & CRITICAL_MARKERS)
        if critical_hits:
            risk += 4 + critical_hits
        if token_set & HIGH_MARKERS:
            risk += 2
        if review.rating is not None and review.rating <= 1:
            risk += 1
        if {"return", "support"} & set(aspects):
            risk += 1
        criticality = Criticality.CRITICAL if risk >= 7 else Criticality.HIGH if risk >= 4 else Criticality.MEDIUM if risk >= 2 else Criticality.LOW
        explanation = f"rule_score={score:.2f}; markers={','.join(hits[:8]) or 'none'}; aspects={','.join(aspects)}; criticality={criticality.value}; version={ANALYSIS_VERSION}"
        return AnalysisResult(
            review_id=review.id,
            sentiment=sentiment,
            sentiment_score=round(score, 3),
            confidence=round(confidence, 3),
            aspects=aspects,
            criticality=criticality,
            explanation=explanation,
            analysis_version=ANALYSIS_VERSION,
        )
