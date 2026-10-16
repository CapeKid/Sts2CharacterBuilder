---
name: create-character-dialogue
description: Create Ancient and character dialogue with localization and encounter integration.
---

Ask whether Ancient dialogue is wanted, collect supplied lines and offer AI completion. Record voice, first/repeat encounter, victory/return/ending and languages separately.
Author localization keys and project-owned hooks for the selected branch. Native Ancient cards are separate models and need card/pool verification. Avoid copying the original mod's conversations or progression assumptions.
The baseline generator has no custom Ancient hooks. Implement and test actual encounter selection and fallback lines before declaring this step complete. Verify first/repeat conditions, localization fallback, save/resume and other-character isolation.
Skip outcome: set dialogue false and retain native encounter dialogue; no partial custom hooks.
