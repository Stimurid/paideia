# Agent Working Environment

Before acting in Paideia, an agent should identify:

- active repo root;
- current branch and git status;
- whether the task touches runtime code, prompts, raw corpus, cache, deploy, or docs only;
- whether live LLM/API calls are allowed;
- whether `.env` values are needed. They usually are not.

Safe default:

1. inspect status;
2. name the working surface;
3. keep source corpus and runtime prompts as data unless approved;
4. preserve rollback;
5. report honest status, not fake done.
