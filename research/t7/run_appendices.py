#!/usr/bin/env python3
from __future__ import annotations

import subprocess
from pathlib import Path

import build_appendices as base


DIAGRAMS = {
    "appendix_a_corpus": r'''
rankdir=LR;
A [label="Публичные источники\nYandex Maps + RuStore"];
B [label="Проверка периода\nи пригодности"];
C [label="Удаление дублей\nи обезличивание"];
D [label="Пригодный пул\n1302 записи"];
E [label="Детерминированный отбор"];
F [label="Итоговый корпус\n1200 отзывов\n1192 + 8"];
A -> B -> C -> D -> E -> F;
''',
    "appendix_e_tobe": r'''
rankdir=TB;
A [label="Получение"];
B [label="Регистрация + происхождение данных"];
C [label="Валидация / дубли / ПДн"];
D [label="Классификация"];
E [label="Проверка C3/C4"];
F [label="Маршрутизация"];
G [label="Решение"];
H [label="Ответ"];
I [label="Мероприятие"];
J [label="Контроль"];
K [label="Подтверждённый результат"];
L [label="Закрытие / знания / аналитика"];
A -> B -> C -> D -> E -> F -> G;
G -> H;
G -> I;
H -> J;
I -> J;
J -> K -> L;
''',
    "appendix_i_decision": r'''
rankdir=TB;
A [label="Новый отзыв"];
B [label="Классификация"];
C [label="Критерий критичности?", shape=diamond];
D [label="Предварительный C3/C4"];
E [label="Экспертная проверка"];
F [label="Высокий риск подтверждён?", shape=diamond];
G [label="Эскалация"];
H [label="Изменить уровень с основанием"];
I [label="Стандартная маршрутизация"];
J [label="Решение"];
K [label="Ответ и/или мероприятие"];
L [label="Контроль"];
M [label="Результат подтверждён?", shape=diamond];
N [label="Закрытие"];
A -> B -> C;
C -> D [label="да"];
C -> I [label="нет"];
D -> E -> F;
F -> G [label="да"];
F -> H [label="нет"];
G -> J;
H -> J;
I -> J;
J -> K -> L -> M;
M -> J [label="нет"];
M -> N [label="да"];
''',
    "appendix_k_arch": r'''
rankdir=LR;
A [label="Каналы"];
B [label="Регистрация"];
C [label="Качество данных"];
D [label="Классификация"];
E [label="Решение / маршрутизация"];
F [label="Коммуникация"];
G [label="Мероприятия"];
H [label="Контроль результата"];
I [label="Аналитика / KPI"];
J [label="База знаний"];
A -> B -> C -> D -> E;
E -> F;
E -> G;
F -> H;
G -> H;
H -> I -> J -> D;
''',
    "appendix_n_impl": r'''
rankdir=LR;
E0 [label="E0\nРешение"];
E1 [label="E1\nПодготовка"];
E2 [label="E2\nАдаптация"];
E3 [label="E3\nОбучение"];
E4 [label="E4\nПериод «до»"];
E5 [label="E5\nПилот"];
E6 [label="E6\nИзмерение «после»"];
E7 [label="E7\nОценка"];
D [label="Решение", shape=diamond];
E8 [label="E8\nМасштабирование"];
C [label="Корректировать"];
X [label="Остановить"];
E0 -> E1 -> E2 -> E3 -> E4 -> E5 -> E6 -> E7 -> D;
D -> E8 [label="масштабировать"];
D -> C [label="корректировать"];
D -> X [label="остановить"];
''',
}


def safe_dot_png(name: str, _dot_body: str) -> Path:
    if name not in DIAGRAMS:
        raise RuntimeError(f"No canonical appendix diagram registered for {name}")
    dot_path = base.GEN / f"{name}.dot"
    png_path = base.GEN / f"{name}.png"
    dot_path.write_text(
        "digraph G {\n"
        "graph [bgcolor=white, pad=0.2, nodesep=0.35, ranksep=0.5];\n"
        "node [shape=box, style=\"rounded\", fontname=\"DejaVu Sans\", fontsize=10];\n"
        "edge [fontname=\"DejaVu Sans\", fontsize=9];\n"
        + DIAGRAMS[name]
        + "\n}\n",
        encoding="utf-8",
    )
    subprocess.run(
        ["dot", "-Tpng", "-Gdpi=180", str(dot_path), "-o", str(png_path)],
        check=True,
    )
    return png_path


def main() -> None:
    base.dot_png = safe_dot_png
    base.build()


if __name__ == "__main__":
    main()
