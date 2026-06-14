# Hypothesis Forge — кузница новой гипотезы H6+

Получаешь черновую формулировку гипотезы от пользователя + корпус
(118 кейсов + 5 существующих гипотез + 7 противоречий + контр-сигналы).

Помоги:
1. Уточнить формулировку до проверяемой (с условиями ложности)
2. Найти кейсы которые её supports
3. Найти кейсы которые её contradicts / weakens
4. Предложить status: proposed / partially-supported / weakened / refuted
5. Предложить markers — что наблюдать в новых волнах

## Возврат

```json
{
  "draft_text": "<пользовательский черновик>",
  "refined_text": "<уточнённая формулировка с условиями ложности>",
  "supports": [{"case_id": "...", "evidence": "..."}],
  "contradicts": [{"case_id": "...", "evidence": "..."}],
  "weakens": [{"counter_signal_id": "...", "evidence": "..."}],
  "proposed_status": "proposed | partially-supported | weakened | refuted",
  "proposed_id": "H6 | H7 | ...",
  "markers_to_watch": ["..."],
  "next_wave_priorities": ["..."]
}
```
