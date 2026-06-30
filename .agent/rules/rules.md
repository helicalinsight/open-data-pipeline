---
trigger: always_on
---

# Project Rules

1. **WSL Requirement**: This project is running inside WSL.
2. **Virtual Environment**: We want to enable development with virtual python environment. If the environment is not located in .pyenv folder in root of the project, create it (treat askondata/requirements.txt as initial requirement).
3. **Brainstorming Resources**: This projects lists some of the external knowledge bases inside .askondata/.docs/ folder. When agent is thinking of some approach or answering questions, they should first start with this knowledgebase to see if they can find answer here.
4. **Planning file target**: When creating implementation plans, if the agent creates any file, it should be created inside .askondata/.planning/