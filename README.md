  <h1  style="border-color:#219db5;width:100%;border-width:2px;text-align:center;margin-left:0"> 
  <code style="color:#219db5;">dawgpyl</code> 
  - Directing Agents with Graphs Python Library
  </h1>

<span style="font-size:120%;text-align:center;">

<!-- <table align="center">
  <tr>
    <td>
      <ins> <i>Developed with</i> <b> ♥ </b>by</ins>:<br>
      <b>Erik L. Hodges, PhD.<b> 
      <br> 
      <a href=https://www.linkedin.com/in/erikhodges>LinkedIn</a>  
      /  
      <a href=https://github.com/ErikHodges>GitHub</a>
    </td>
    <td>
      <a href="https://www.ErikHodges.com"><img src="docs/assets/EH_Logo.png" width="60"></a>
    </td>
    </tr>
</table> -->

| <ins> _Developed with_ **♥** _by_</ins>:  <br>**Erik L. Hodges, PhD.** <br> [**LinkedIn**](https://www.linkedin.com/in/erikhodges/)  /  [**GitHub**](https://github.com/ErikHodges)  |  <a href="https://www.ErikHodges.com"><img src="docs/assets/EH_Logo.png" width="60"></a> |
|---|---|

</span>

<hr style="border-color:#219db5;width:100%;border-width:2px;text-align:left;margin-left:0">

<div id="navigation">
<span style="font-size:120%;font-weight:bold;text-align:center;">


<a href=https://ErikHodges.github.io/dawgpyl>Documentation</a><br>
<a href=#overview>Overview</a><br>
<a href=#how_dawgpyl_works>How <code style="color:#219db5">dawgpyl</code> Works</a><br>
<a href=#quickstart>Quickstart</a><br>


<hr style="border-color:#219db5;width:100%;border-width:2px;text-align:left;margin-left:0">

</span>
</div>



<div id="overview" >
<details><summary><h2 style="display:inline-block;border-color:rgba(0,0,0,0)">
Overview
</h2></summary>

- Recent advances in large language models (LLMs) have made these systems capable of outputting structured content.
- Leveraging structured inputs and outputs, LLM-based `Agents` can be made to consistenly execute dynamic workflows.
- The <code style="color:#219db5;">dawgpyl</code> library provides a common framework to configure `Agents` and orchestrate interactions between `Teams`.
- Simply put, a user can define a goal and a `Teams` of `Agents` will work to accomplish it.
- Each `Agent` can be configured to guide and constrain its behaviors to suit your needs.

<br>

> [!CAUTION]
> Agent responses are stochastic<br>You are responsible for ensuring agents exhibit desired behaviors<br>**Always review outputs**  


</details></div>

<hr style="border-color:#219db5;width:100%;border-width:2px;text-align:left;margin-left:0">


<div id="how_dawgpyl_works">
<details><summary><h2 style="display:inline-block;border-color:rgba(0,0,0,0)">
How <code style="color:#219db5;">dawgpyl</code> works
</h2></summary>



### Core Classes

<span style="font-size:100%;font-weight:normal">

- `Prompt` ( `PromptSystem` , `PromptUser`, `ResponseFormat` )

- `Task` ( `Prompt` )

- `Agent` ( `Task`)

- `Team`( [
      `Agent`<sub style="font-size:75%;font-weight:normal">1</sub>,
      `Agent`<sub style="font-size:75%;font-weight:normal">2</sub>,
      `Agent`<sub style="font-size:75%;font-weight:normal">3</sub>,
      **...**
      ]
)
- `Project`(
      [
        `Team`<sub style="font-size:75%;font-weight:normal">1</sub>,
        `Team`<sub style="font-size:75%;font-weight:normal">2</sub>,
        **...**
        ]
)
<br><br>

<!-- ---
#### Expression
$Result = Project(
  [
    Team(
      [
        Agent_1(Task_1(PromptSystem_1,PromptUser_1,ResponseFormat_1)),
        Agent_2(Task_2(PromptSystem_2,PromptUser_2,ResponseFormat_2)),
        Agent_3(Task_3(PromptSystem_3,PromptUser_3,ResponseFormat_3)),
      ],
    ),
    Team(
      [
        Agent_4(Task_4(PromptSystem_4,PromptUser_4,ResponseFormat_4)),
        Agent_5(Task_5(PromptSystem_5,PromptUser_5,ResponseFormat_5)),
      ],
    ),
  ]
)
$ -->


---
- `APIs`
  - Application program interface (API) to a model or tool provider
  - Often requires you to register an account and create an API key
  - API keys are stored in
    - `configs/apis.py`
<br>

---
- `Model`
  - A specific version of a model
    - (e.g., "gpt-4", "4o", "claude-3.7", "deepseek-r1")
  - **Currently supported model types**: ["embedding","llm"]
- `ModelConfig`
  - `configs/models.py`
<br>
---

<!-- - `Persona`
  - A general role that is assigned to an `Agent`

---
 -->

- `Agent` 
  - Single instances of an LLM-client (i.e., a chat).
  - An `Agent` is given a `Task`
- `AgentConfig`
  - Name
  - Model
  - Persona
  - Task
  - ~~Team~~ **?????**
<br>
---

- `Tasks`
- `TaskConfig`
<br>
---

- `Teams` 
  - Groups of `Agents`
  - `Teams` are given `Goals`
- `TeamConfig`
  - Name: "Research"
  - Supervisor: `Agent`
  - Members: [`Agent`,`Agent`]
  - Goal: "Please produce a cohesive report summarizing the reasons that Erik is a cool guy"
  - Log: [{`Target`:`Event`},{`Target`:`Event`}]
<br>

<!-- 
note: This feels unnecessary, since I already have a `Team` collection.
note: IF it is possible that a Team's members can be a collection of teams, then this will work!
- `Projects` 
  - Groups of `Teams`
  - `Projects` are given `Milestones`
- `ProjectConfig`
  - Name: "Application development"
  - Supervisor: `Agent`
  - Members: [`Team`,`Team`]
<br><br> -->

</span>

---
### Architecture

<img src="docs/assets/architecture.svg" width="1024"/>
<br>

</details></div>

<hr style="border-color:#219db5;width:100%;border-width:2px;text-align:left;margin-left:0">

<div id="quickstart">
<details><summary><h2 style="display:inline-block;border-color:rgba(0,0,0,0)">Quickstart
</h2></summary>

### 0. Requirements 
- Skills
  - Basic understanding of python programming
- Programmatic access to an LLM (API key)
  - OpenAI
  - Anthropic
- Software
  - git
  - python 3.11
- [Documentation](https://erikhodges.github.io/dawgpyl/)
  - (Offline) view the docs in your browser using the [mkdocs library](https://www.mkdocs.org/)
    > ```bash
    > # install mkdocs
    > pip install -U mkdocs
    > # Navigate to the dawgpyl directory
    > cd dawgpyl
    > # Serve the documents
    > mkdocs serve
    > ```


### 1. Clone the <code style="color:#219db5;">dawgpyl</code> repository to your local machine

> ```bash
> # Navigate to the directory you use to develop code
> cd YOUR_CODE_DIRECTORY
> git clone https://github.com/ErikHodges/dawgpyl.git
> ```

### 2. Create a virtual environment and activate it

- **Windows**
  > ```bash
  > # Navigate to the directory where you cloned the repository
  > cd YOUR_CODE_DIRECTORY/dawgpyl
  > python -m venv dpenv
  > dpenv/Scripts/activate
  > ```

- **Linux**
  > ```bash
  > # Navigate to the directory where you cloned the repository
  > cd YOUR_CODE_DIRECTORY/dawgpyl
  > python -m venv dpenv
  > dpenv/bin/activate
  > ```

### 3. Install <code style="color:#219db5;">dawgpyl</code> dependencies

> ```bash
> # Navigate to the directory where you cloned the repository  
> python -m pip install --upgrade pip
> python -m pip install .
> ```


### 4. Open the quickstart notebook

> ```bash
> # Run the 01_COPILOT.ipynb file
> notebooks/01_COPILOT.ipynb
> ```
<br>

---

> [!TIP]
> `Teams` of `Agents` can be configured to follow standardized workflows.


</details></div>

<hr style="border-color:#219db5;width:100%;border-width:2px;text-align:left;margin-left:0">





<div id="documentation_offline">
<details><summary><h2 style="display:inline-block;border-color:rgba(0,0,0,0)">Documentation (offline)</h2></summary>




</details></div>

<hr style="border-color:#219db5;width:100%;border-width:2px;text-align:left;margin-left:0">

