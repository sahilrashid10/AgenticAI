# Customer Onboarding Agent Suite

This repository contains multiple versions of a customer onboarding workflow built with different agentic AI frameworks. Each subfolder shows the same business idea implemented in a different style so you can compare how CrewAI, LangChain, LangGraph, and Semantic Kernel handle orchestration, tools, and state.

## What This Project Does

The goal is to onboard a customer by following a simple workflow:

1. Validate the customer details.
2. Check whether the customer already exists.
3. Save the customer if they are new.
4. Generate onboarding communication.
5. Show the result in a clean terminal flow.

The project is useful for learning how different frameworks structure the same problem.

## Folder Overview

### `crewai/`

CrewAI version of the onboarding system.

- `config/` contains app settings and prompt text.
- `crew/` contains the agents, tasks, and crew orchestration.
- `data/` stores customer records in JSON format.
- `models/` contains the customer data model.
- `tools/` contains CrewAI-compatible tools for validation and saving.
- `utils/` contains database and logging helpers.
- `main.py` is the entry point for running the workflow.
- `requirements.txt` lists the dependencies for this version.

This version is built around the CrewAI pattern of agents plus tasks.

### `langchain/`

LangChain version of the onboarding system.

- `config/` contains prompt and settings files.
- `data/` stores customer records.
- `models/` contains the customer schema.
- `tools/` contains LangChain tools for validation and persistence.
- `utils/` contains database and logging helpers.
- `main.py` runs the LangChain flow.
- `requirements.txt` lists dependencies.

This version is useful for understanding agent tool calls and prompt-driven orchestration.

### `langgraph/`

LangGraph version of the onboarding system.

- `config/` contains prompt and settings files.
- `data/` stores customer records.
- `graph/` contains the nodes, state, and workflow definition.
- `models/` contains the customer schema.
- `utils/` contains database and logging helpers.
- `main.py` runs the graph workflow.

This version focuses on explicit state transitions and node-based orchestration.

### `semantic_kernel/`

Semantic Kernel version of the onboarding system.

- `config/` contains prompt and settings files.
- `data/` stores customer records.
- `models/` contains the customer schema.
- `plugins/` contains the customer plugin used by the kernel.
- `utils/` contains database, helper, and logging utilities.
- `main.py` runs the Semantic Kernel workflow.
- `requirements.txt` lists dependencies.

This version shows a plugin-first approach where the kernel coordinates the logic.

### `notes`

This file contains short learning notes comparing the frameworks and explaining concepts such as:

- `agent_scratchpad`
- Pydantic validation
- the difference between kernels, agents, graphs, and crews
- how validation and error handling are usually handled in this project

## Workflow Summary

The customer onboarding flow is intentionally simple:

- Validate the input.
- Stop if the email or required data is wrong.
- Check for an existing customer.
- Save the customer if they are new.
- Generate onboarding output.

In the CrewAI version, this is handled by agents and tasks.
In LangChain, it is handled by tools and agent prompts.
In LangGraph, it is handled by nodes and shared state.
In Semantic Kernel, it is handled by plugins managed by the kernel.

## Screenshots

### CrewAI Run

This screenshot shows the CrewAI folder opened in VS Code and the crew execution starting from the terminal.

![CrewAI run screenshot](crewai/Screenshot%20(727).png)

### LangGraph Flow

This screenshot shows the LangGraph workflow diagram with validation, existence check, saving, email generation, and error branches.

![LangGraph flow screenshot](langgraph/Screenshot%202026-07-11%20153815.png)

## How to Run

Each framework folder has its own `main.py`, and you should run the one you want to test.

Example:

```powershell
py customer_onboarding\crewai\main.py
py customer_onboarding\langchain\main.py
py customer_onboarding\langgraph\main.py
py customer_onboarding\semantic_kernel\main.py
```

## Installation

Use the requirements file inside the folder you want to run.

Example:

```powershell
pip install -r customer_onboarding\crewai\requirements.txt
pip install -r customer_onboarding\langchain\requirements.txt
pip install -r customer_onboarding\semantic_kernel\requirements.txt
```

## Project Structure

```text
customer_onboarding/
├── crewai/
│   ├── config/
│   ├── crew/
│   ├── data/
│   ├── models/
│   ├── tools/
│   ├── utils/
│   ├── main.py
│   └── requirements.txt
├── langchain/
│   ├── config/
│   ├── data/
│   ├── models/
│   ├── tools/
│   ├── utils/
│   ├── main.py
│   └── requirements.txt
├── langgraph/
│   ├── config/
│   ├── data/
│   ├── graph/
│   ├── models/
│   ├── utils/
│   └── main.py
├── semantic_kernel/
│   ├── config/
│   ├── data/
│   ├── models/
│   ├── plugins/
│   ├── utils/
│   ├── main.py
│   └── requirements.txt
└── notes
```

## Why There Are Multiple Frameworks

The repo is meant to compare the same business workflow across different AI orchestration styles.

- CrewAI is best for agent and task workflows.
- LangChain is best for tool-driven agent behavior.
- LangGraph is best when you want explicit graph state and branching.
- Semantic Kernel is best when you want a kernel plus plugin structure.

## Learning Notes

This project is a good comparison exercise because it shows how each framework handles:

- validation
- tool use
- persistence
- sequential flow
- error handling
- state passing

## License

Add your preferred license here before publishing on GitHub.

## Author

Created as part of an agentic AI learning project.