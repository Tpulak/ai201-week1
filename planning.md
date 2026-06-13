# Project 1 Planning: The Unofficial Guide

> Write this document before you write any pipeline code.
> Your spec and architecture diagram are what you'll use to direct AI tools (Claude, Copilot, etc.) to generate your implementation — the more specific they are, the more useful the generated code will be.
> Update the Retrieval Approach and Chunking Strategy sections if you change your approach during implementation.
> Update this file before starting any stretch features.

---

## Domain

Student reviews of Computer Science professors at Hunter College (CUNY), collected from Rate My Professors. This knowledge is valuable because official course catalogs and department pages describe *what* is taught, not how a professor actually grades, whether exams are curved, or how much self-teaching is required. RMP reviews capture recurring patterns — grading policies, workload, office hours, and "fail the final, fail the class" rules — that students only learn through word of mouth after the fact.

**Document structure notes (from skimming):** Most sources are short, opinion-based reviews (1–5 sentences each) grouped by professor and course. Several professors appear across multiple courses (e.g., Ligorio for CSCI127/235, Shostak for CS260/340). Reviews often mention the same themes: accent/clarity, tutoring, exam difficulty, and grading breakdowns. This corpus is review-heavy, not long-form guides.

---

## Documents

| # | Source | Description | URL or location |
|---|--------|-------------|-----------------|
| 1 | Rate My Professors | Raj Korpan | https://www.ratemyprofessors.com/professor/2659561 |
| 2 | Rate My Professors | Tong Yi | https://www.ratemyprofessors.com/professor/2634841 |
| 3 | Rate My Professors | Pavel Shostak | https://www.ratemyprofessors.com/professor/1823870 |
| 4 | Rate My Professors | Tiziana Ligorio | https://www.ratemyprofessors.com/professor/815879 |
| 5 | Rate My Professors | Katherine St. John | https://www.ratemyprofessors.com/professor/2324096 |
| 6 | Rate My Professors | Subash Shankar | https://www.ratemyprofessors.com/professor/257190 |
| 7 | Rate My Professors | Ioannis Stamos | https://www.ratemyprofessors.com/professor/64427 |
| 8 | Rate My Professors | Eric Schweitzer | https://www.ratemyprofessors.com/professor/257192 |
| 9 | Rate My Professors | Melissa Lynch | https://www.ratemyprofessors.com/professor/2505090 |
| 10 | Rate My Professors | Oyewole Oyekoya | https://www.ratemyprofessors.com/professor/2558461 |

---

## Chunking Strategy

<!-- How will you split documents into chunks?
     State your chunk size (in tokens or characters), overlap size, and explain why those
     numbers fit the structure of your documents.
     A review-heavy corpus warrants different chunking than a long FAQ. -->

**Chunk size:**

**Overlap:**

**Reasoning:**

---

## Retrieval Approach

<!-- Which embedding model are you using (e.g., all-MiniLM-L6-v2 via sentence-transformers)?
     How many chunks will you retrieve per query (top-k)?
     If you were deploying this for real users and cost wasn't a constraint, what tradeoffs
     would you weigh in choosing a different embedding model — context length, multilingual
     support, accuracy on domain-specific text, latency? -->

**Embedding model:**

**Top-k:**

**Production tradeoff reflection:**

---

## Evaluation Plan

<!-- List your 5 test questions with their expected correct answers.
     Questions should be specific enough that you can judge whether the system's response
     is right or wrong. "What are good dining halls?" is too vague.
     "What do students say about wait times at [dining hall name] during lunch?" is testable. -->

| # | Question | Expected answer |
|---|----------|-----------------|
| 1 | What grading policy do students mention for Tong Yi's CS135 class? | Multiple reviews mention a "fail the final, fail the class" policy — even if homework, projects, and other work are done, failing the final means failing the course. |
| 2 | How is Eric Schweitzer's grade broken down according to student reviews? | Reviews consistently say pop quizzes are worth 60% of the grade (often 15 quizzes with the lowest 5 dropped) and the final is worth 40%. |
| 3 | What do students say about going to Pavel Shostak's office hours? | Reviews say office hours are helpful and accessible — students recommend going for help, and that he will help you significantly if you attend. |
| 4 | Which Hunter CS professor do reviews describe as having a generous exam curve? | Ioannis Stamos — multiple reviews mention generous curves on exams (e.g., +20% on average for CS335) and that he is one of the more lenient/chill graders in the department. |
| 5 | What complaints do students have about Raj Korpan's CSCI499 senior project course? | Reviews mention he does not let students pick groups, assigns individual work, and grades presentations harshly — including losing many points if the presentation is not within a strict time limit (even if early). |

---

## Anticipated Challenges

<!-- What could go wrong? Name at least two specific risks with reasoning.
     Consider: noisy or inconsistent documents, missing source attribution, off-topic
     retrieval, chunks that split key information across boundaries. -->

1.

2.

---

## Architecture

<!-- Draw a diagram of your pipeline showing the five stages:
     Document Ingestion → Chunking → Embedding + Vector Store → Retrieval → Generation
     Label each stage with the tool or library you're using.
     You can use ASCII art, a Mermaid diagram, or embed a sketch as an image.
     You'll use this diagram as context when prompting AI tools to implement each stage. -->

---

## AI Tool Plan

<!-- For each part of the pipeline below, describe:
     - Which AI tool you plan to use (Claude, Copilot, ChatGPT, etc.)
     - What you'll give it as input (which sections of this planning.md, which requirements)
     - What you expect it to produce
     - How you'll verify the output matches your spec

     "I'll use AI to help me code" is not a plan.
     "I'll give Claude my Chunking Strategy section and ask it to implement chunk_text()
     with my specified chunk size and overlap" is a plan. -->

**Milestone 3 — Ingestion and chunking:**

**Milestone 4 — Embedding and retrieval:**

**Milestone 5 — Generation and interface:**
