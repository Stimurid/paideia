"""Paideia TRIZ-engine — L0-L3 архитектура агентного runtime.

Источник архитектуры: C:/projects/Claude/TRIZ/architecture/ (Inventive Memory
Bench / FifthConstraint / quint). Здесь — Python-перевоплощение для Paideia.

Слои:
- L0 operators — детерминированные функции над SystemModel/Branch
- L1 agents — рабочие LLM-агенты с kernel-промптами
- L2 spaces — пространства активных агентов
- L3 meta-agents — Agent Foundry, Self-Reconfiguration
- Orchestrator — регулятор метастабильности
- AgentRun — process-контейнер с preview/apply/EventLog
"""
