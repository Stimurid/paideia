# Genealogy — родители и дети кейса/проекта

Получаешь SystemModel или case + полный корпус (id + title + pattern + agentivity + tags).

Найди **родителей** (кейсы которые повлияли на дизайн этого, или
исторически предшествовали) и **детей** (кейсы которые развили эту идею
дальше, или могут от неё произойти).

## Возврат

```json
{
  "subject_id": "...",
  "parents": [
    {"case_id": "...", "relation": "evolved_from | inspired_by | adapted_from", "evidence": "..."}
  ],
  "siblings": [
    {"case_id": "...", "shared_pattern": "...", "key_difference": "..."}
  ],
  "children": [
    {"case_id": "...", "relation": "extends | radicalizes | mainstreams", "evidence": "..."}
  ],
  "evolution_line": "<куда движется эта линия за 3-5 лет>"
}
```
