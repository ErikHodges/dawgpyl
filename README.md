# dawgpyl

Directing Agents With Graphs Python Library

[**Documentation**](https://ErikHodges.github.io/dawgpyl/)

---

<!-- <center>   -->

`<u>`_Developed with_ **♥** _by_:`</u>`
**Erik L. Hodges, PhD.**
[**LinkedIn**](https://www.linkedin.com/in/erikhodges/)  /  [**GitHub**](https://github.com/ErikHodges)

[`<img src="docs/assets/EH_Logo.png" width="100"/>`](https://www.ErikHodges.com)

<!-- </center> -->

## Description

- Recent advances in large language models (LLMs) are capable of reliably outputting structured content.
- Leveraging structured inputs and outputs, LLM-based *agents* can be made to consistenly execute dynamic workflows.
- This library provides a common framework to orchestrate interactions between these agents in such a way that a user can define a goal and a team of agents will work to accomplish it.
- Each agent (team-member) can be customized to guide and bound its behavior to suit your desired task and needs.

> [!CAUTION] CAUTION - LLM outputs are stochastic
> Care must be taken to ensure that agents exhibit the desired behavior.
> `<u>` Always review outputs `</u>`

## Requirements

- Skills
  - Basic understanding of python programming
- Programmatic access to an LLM (API key)
  - OpenAI
  - Anthropic
- Software
  - Git
  - python 3.11
  - jupyter notebook

<br>

## Quickstart

### Clone the `dawgpyl` repository to your local machine

> ```bash
> # Navigate to the directory you use to develop code
> cd YOUR_CODE_DIRECTORY
> git clone https://github.com/ErikHodges/dawgpyl.git
> ```

### Create a virtual environment and activate it

#### Windows

> ```bash
> # Navigate to the directory where you cloned the repository
> cd YOUR_CODE_DIRECTORY/dawgpyl
> python -m venv dpenv
> dpenv/Scripts/activate
> ```

#### Linux

> ```bash
> # Navigate to the directory where you cloned the repository
> cd YOUR_CODE_DIRECTORY/dawgpyl
> python -m venv dpenv
> dpenv/bin/activate
> ```

### Install `dawgpyl` dependencies

> ```bash
> # Navigate to the directory where you cloned the repository  
> python -m pip install --upgrade pip
> python -m pip install .
> ```

### Open the quickstart notebook

> ```bash
> # Run the 01_COPILOT.ipynb file
> notebooks/01_COPILOT.ipynb
> ```

### Agents

In `dawgpyl`, an `Agent` is simply an instance of an LLM-client (i.e. a connection to an LLM).

### Agent Configuration

### Task configuration

- `configs/agents.py`
- `configs/prompts.py`

Projects > Teams > Agents (individual LLMs)

> [!TIP] Advanced
> Teams of agents can be pre-specified to follow standardized workflows.
>
> - ``configs/projects.py``
> - ``configs/teams.py``

---

## Documentation

> [!TIP] Documentation can be viewed in your browser using the mkdocs library
>
> ```bash
> # install mkdocs
> pip install -U mkdocs
> # Navigate to the dawgpyl directory
> cd dawgpyl
> # Serve the documents
> mkdocs serve
> ```

## Architecture

<img src="docs/assets/architecture.svg" width="1024"/>
