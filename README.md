# The Unofficial Guide — Project 1

> Student reviews of Hunter College CS professors, searchable via RAG.

---

## Domain

Student reviews of Computer Science professors at Hunter College (CUNY), collected from Rate My Professors. This information is valuable because students often want to know what a professor's class is actually like — workload, teaching style, grading, exams, and how much self-study is needed. It is hard to find through official channels because course catalogs only describe content, not the real student experience across different professors.

---

## Document Sources

| # | Source | Type | URL or file path |
|---|--------|------|-----------------|
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

Raw text files live in `documents/`. Ingestion is handled by `ingest.py`.

---

## Chunking Strategy

**Chunk size:** One complete RMP review per chunk (~250–500 characters of review text, plus metadata: professor name, course, quality/difficulty, date). Each chunk is one `Review N` block — not a fixed character split.

**Overlap:** 0 characters. Reviews are self-contained; overlap would duplicate professor/course context without helping retrieval.

**Why these choices fit your documents:** The corpus is review-heavy (short opinions, not long guides). Average review length is ~311 characters across ~792 reviews. Splitting by review boundary keeps each embedding focused on one student's take on one course. Professor and class are prepended to each chunk so queries like "Tong Yi CS135" match even when the review body omits the name.

**Preprocessing:** Strip `Likes:` / `Dislikes:` lines, decorative separators, and banner lines. Keep professor, class, quality, difficulty, date, and review text.

**Final chunk count:** 792

**Sample chunk** (from `rmp_eric_schweitzer.txt`):

```text
Professor: Eric Schweitzer
Source: rmp_eric_schweitzer.txt
Class: CS265
Quality: 2.0 | Difficulty: 4.0
Date: May 25th, 2025
Review: Not the best & not the worst. Class is entirely based on pop quizzes. There are 15 pop quizzes worth 60% of your grade, the lowest 5 get dropped. Final is worth 40% & based on quizzes...
```

---

## Embedding Model

**Model used:** `all-MiniLM-L6-v2` via `sentence-transformers` (runs locally, no API key). Loaded in `retrieve.py` with `SentenceTransformer("all-MiniLM-L6-v2")`. Each chunk's full `text` field is embedded into a 384-dimensional vector.

**How vectors are stored:** Vectors are written to a local ChromaDB collection (`chroma_db/`, collection name `professor_reviews`) along with metadata: `source_file`, `professor`, `class_name`, `chunk_index`, `review_number`, and `source_url`.

**Production tradeoff reflection:** If cost were not a constraint, I would weigh: (1) accuracy on short informal review text — MiniLM is fine for a class project but a review-tuned or larger model might match student phrasing better; (2) multilingual support for ESL-related reviews; (3) context length — less critical here since chunks are short; (4) latency vs. quality for API-hosted embedders; (5) local vs. hosted — MiniLM avoids cost and rate limits but requires re-embedding when documents change.

---

## Retrieval Test Results (Milestone 4)

### How to run retrieval tests

From the project root, with dependencies installed:

```powershell
cd C:\Users\Pulak\Desktop\codepath\codepath-ai201\week1\ai201-week1
python retrieve.py
```

**Notes:**
- Use `python` (Miniconda) if your `.venv` hits a PyTorch DLL error on Windows.
- First run embeds all 792 chunks and creates `chroma_db/` (may take 1–2 minutes while the model downloads).
- Later runs print `ChromaDB index already contains 792 chunks.` and jump straight to the three test queries.
- Full output is also saved in `retrieve_run_output.txt`.

The script prints:
1. Index build progress (`Stored 64/792` … `Stored 792/792`)
2. Three eval queries with top-5 chunks, distance scores, professor, source file, and review preview

---

### What distance scores mean

When you ask a question, retrieval does **not** compare raw text word-by-word. It compares **meaning vectors**:

1. **Embed the query** — `all-MiniLM-L6-v2` converts your question into a 384-number vector (same model used for chunks).
2. **Compare to every stored chunk vector** — ChromaDB finds the vectors closest to the query vector.
3. **Return a distance score** — ChromaDB uses **L2 (Euclidean) distance** by default: roughly, how far apart the query vector and chunk vector are in 384-dimensional space.

**How to read the number:**

| Distance | Meaning |
|----------|---------|
| **Lower = better** | Smaller distance → chunk meaning is closer to the query |
| **~0.0–0.5** | Strong match (assignment guideline for good retrieval) |
| **~0.5–0.7** | Moderate / fuzzy match — related topic but not always the exact fact |
| **> 0.7** | Weak match — often wrong professor or off-topic |

We do **not** calculate distance manually in Python. `retrieve.py` calls `collection.query(query_embeddings=...)` and ChromaDB returns the `distances` list alongside the matched documents.

**Why semantic search works:** The model places similar *meanings* near each other even when words differ — e.g. "pop quiz grading" and "60% of your grade from quizzes" can end up close in vector space.

---

### Query 1 — Tong Yi CS135 grading policy

**Query:** `What grading policy do students mention for Tong Yi's CS135 class?`

**Expected:** Reviews mention a **"fail the final, fail the class"** policy.

| Rank | Professor | Source | Distance | Top review snippet |
|------|-----------|--------|----------|-------------------|
| 1 | Tong Yi | `rmp_tong_yi.txt` | 0.6133 | Pass tips; mentions scoring 60 on the final |
| 2 | Tong Yi | `rmp_tong_yi.txt` | 0.6193 | General complaints about instructions |
| 3 | Tong Yi | `rmp_tong_yi.txt` | 0.6600 | "Easy grade" review |
| 4 | Tong Yi | `rmp_tong_yi.txt` | 0.6715 | Failing the class emotionally, not policy text |
| 5 | Tong Yi | `rmp_tong_yi.txt` | 0.6830 | Lectures disorganized |

**Retrieval quality:** Partially relevant

**Why the top chunks are (somewhat) relevant:** Every result is from the correct professor and file, and several discuss finals and grading. Result 1 is relevant to grading policy in a broad sense.

**Gap:** None of the top 5 surfaced the specific "fail the final, fail the class" phrase, even though other Tong Yi chunks contain it. Distances (0.61–0.68) are above the ~0.5 ideal — the query matched general grading talk, not that specific policy wording.

---

### Query 2 — Eric Schweitzer grade breakdown

**Query:** `How is Eric Schweitzer's grade broken down according to student reviews?`

**Expected:** Pop quizzes ≈ **60%** (often 15 quizzes, lowest 5 dropped); final ≈ **40%**.

| Rank | Professor | Source | Distance | Top review snippet |
|------|-----------|--------|----------|-------------------|
| 1 | Eric Schweitzer | `rmp_eric_schweitzer.txt` | 0.5374 | Pop quizzes = 60% of grade |
| 2 | Eric Schweitzer | `rmp_eric_schweitzer.txt` | 0.5854 | Exam rubric complaint |
| 3 | Eric Schweitzer | `rmp_eric_schweitzer.txt` | 0.5940 | **"15 pop quizzes worth 60%... Final is worth 40%"** |
| 4 | Eric Schweitzer | `rmp_eric_schweitzer.txt` | 0.5952 | Teaching style, not breakdown |
| 5 | Eric Schweitzer | `rmp_eric_schweitzer.txt` | 0.5962 | 15 quizzes, highest 10 counted |

**Retrieval quality:** Relevant

**Why the top chunks are relevant:** All five are Eric Schweitzer reviews from the correct source file. Results 1 and 3 directly state the 60%/40% split the eval question targets. Result 5 adds related quiz-count detail. This is the strongest retrieval result of the three tests.

---

### Query 4 — Generous exam curve

**Query:** `Which Hunter CS professor do reviews describe as having a generous exam curve?`

**Expected:** **Ioannis Stamos** — generous curves (e.g. +20% on CS335), lenient/chill grader.

| Rank | Professor | Source | Distance | Top review snippet |
|------|-----------|--------|----------|-------------------|
| 1 | Pavel Shostak | `rmp_pavel_shostak.txt` | 0.7186 | "Grading can be tricky" — tough grader tags |
| 2 | Pavel Shostak | `rmp_pavel_shostak.txt` | 0.7208 | Teaching style complaints |
| 3 | Pavel Shostak | `rmp_pavel_shostak.txt` | 0.7271 | Syllabus / honesty complaints |
| 4 | Eric Schweitzer | `rmp_eric_schweitzer.txt` | 0.7586 | Unrelated negative review |
| 5 | Pavel Shostak | `rmp_pavel_shostak.txt` | 0.7597 | "Tough grader" tag |

**Retrieval quality:** Off-target

**Why this failed:** The question asks for a **comparison across all professors** ("which professor…"), but many reviews mention "grading" in negative contexts. Shostak has a large review set with heavy grading language, so those vectors crowded out Stamos reviews that use different phrasing ("huge curve", "+20%", "#thechiller"). No Stamos chunk appeared in the top 5. Distances (0.72–0.76) indicate weak matches overall.

---

## Grounded Generation

Implemented in `query.py` (`ask()`) and exposed through `app.py` (Gradio UI).

**Pipeline:** user question → `retrieve()` (top 5 chunks) → Groq `llama-3.3-70b-versatile` with a strict system prompt → answer + source file list.

**System prompt grounding instruction:**

```text
Answer the user's question using ONLY the information in the provided document excerpts.

Rules:
- Do not use outside knowledge, assumptions, or information not present in the excerpts.
- If the excerpts do not contain enough information to answer the question, respond with exactly:
  "I don't have enough information on that."
- When you use information from an excerpt, name the source file (for example, rmp_tong_yi.txt) in your answer.
- If reviews disagree, summarize what students say without treating one opinion as the only truth.
```

Retrieved chunk text is passed in the user message under labeled excerpts (`--- Excerpt N (source: ...) ---`). Temperature is set to `0.2` to reduce creative drift.

**How source attribution is surfaced in the response:**

1. **In the LLM answer** — the system prompt requires naming source files when using information.
2. **In the UI / return value** — `ask()` also returns a programmatic `sources` list (unique `source_file` values from retrieved chunks), displayed in the Gradio **Retrieved from** box.

**Example responses (from `python query.py`):**

*In-scope — Eric Schweitzer grade breakdown:*
> According to the student reviews in rmp_eric_schweitzer.txt… In CS265, there are 15 pop quizzes worth 60% of the grade, with the lowest 5 dropped, and the final is worth 40%.

*In-scope — Pavel Shostak office hours:*
> According to the excerpts from rmp_pavel_shostak.txt, students say that Professor Pavel Shostak has "very good office hours"…

*Out-of-scope — dining halls:*
> I don't have enough information on that.

---

## Query Interface

**How to run:**

```powershell
cd C:\Users\Pulak\Desktop\codepath\codepath-ai201\week1\ai201-week1
python app.py
```

Open **http://localhost:7860** in your browser.

**Input:** `Your question` — a plain-language question about Hunter CS professors (text box).

**Output:**
- `Answer` — grounded response from Groq using retrieved review excerpts
- `Retrieved from` — bullet list of source files used for retrieval (e.g. `• rmp_eric_schweitzer.txt`)

**Sample interaction:**

| Field | Content |
|-------|---------|
| **Question** | How is Eric Schweitzer's grade broken down according to student reviews? |
| **Answer** | In CS265, reviews in rmp_eric_schweitzer.txt say 15 pop quizzes are worth 60% (lowest 5 dropped) and the final is worth 40%. |
| **Retrieved from** | • rmp_eric_schweitzer.txt |

---

## Evaluation Report

*(Full end-to-end eval with LLM responses — Milestone 6. Retrieval-only results for questions 1, 2, and 4 are documented above.)*

| # | Question | Expected answer | System response (summarized) | Retrieval quality | Response accuracy |
|---|----------|-----------------|------------------------------|-------------------|-------------------|
| 1 | Tong Yi CS135 grading policy | Fail the final, fail the class | *(M5 pending)* | Partially relevant | *(M6 pending)* |
| 2 | Eric Schweitzer grade breakdown | 60% pop quizzes, 40% final | *(M5 pending)* | Relevant | *(M6 pending)* |
| 3 | Pavel Shostak office hours | Helpful, go to office hours | *(M5 pending)* | *(not tested in M4)* | *(M6 pending)* |
| 4 | Professor with generous exam curve | Ioannis Stamos | *(M5 pending)* | Off-target | *(M6 pending)* |
| 5 | Raj Korpan CSCI499 complaints | Groups, presentations | *(M5 pending)* | *(not tested in M4)* | *(M6 pending)* |

---

## Failure Case Analysis

**Question that failed:** `Which Hunter CS professor do reviews describe as having a generous exam curve?` (Eval question 4)

**What the system returned:** Top 5 chunks were mostly **Pavel Shostak** reviews about tough grading and teaching style. **Ioannis Stamos** (who has multiple reviews mentioning generous curves) did not appear in the top 5.

**Root cause (tied to a specific pipeline stage):** **Retrieval / embedding stage.** This is a cross-professor comparison query, but semantic search returns individually similar chunks, not a aggregated "best professor for X" answer. Shostak's corpus is large and contains many "grading" keywords in negative contexts, which scored closer to the query vector than Stamos's more specific curve language ("+20%", "huge curve"). The embedding model also does not know that "tough grader" and "generous curve" are opposites — it matches on shared exam/grading themes.

**What you would change to fix it:** (1) Include professor name in comparison queries at retrieval time; (2) retrieve more chunks (higher k) and dedupe by professor before generation; (3) add metadata filtering when the query implies a specific professor; (4) for "which professor" questions, use a two-step retrieve-then-rank-by-professor approach instead of pure top-k semantic search.

---

## Spec Reflection

*(Milestone 6 — pending.)*

**One way the spec helped you during implementation:**

**One way your implementation diverged from the spec, and why:**

---

## AI Usage

*(Milestone 6 — pending.)*

**Instance 1**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*

**Instance 2**

- *What I gave the AI:*
- *What it produced:*
- *What I changed or overrode:*
