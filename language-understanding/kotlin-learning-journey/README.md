# Learning Kotlin (from Python) — AI-Assisted Journey

**Source language:** Python  
**Target language:** Kotlin  
**Goal:** Build a web API

---

## Learning Journey Plan

### Phase 1: Syntax & Fundamentals
**Prerequisites:** JDK 17+, IntelliJ IDEA Community Edition or Kotlin Playground

1. Basic syntax: `val`/`var`, type inference, string templates
2. Control flow: `if` as expression, `when` (replaces `switch`), loops
3. Functions: named/default args, single-expression functions, lambda syntax
4. Null safety: `?` / `!!` / `?:` Elvis operator — *the biggest shift from Python*
5. Basic I/O and `main()` entry point

**Verify:** Write a CLI that reads a CSV file and prints summary stats.

---

### Phase 2: OOP & Functional Features
**Prerequisites:** Phase 1 comfort

1. Classes: primary/secondary constructors, `data class` (vs Python dataclasses), `sealed class`
2. Inheritance vs composition, `open` keyword, interfaces
3. Collections: `listOf`, `mapOf`, sequences, extension functions
4. Functional programming: `map`, `filter`, `fold`, chaining
5. Scope functions: `let`, `apply`, `run`, `with`, `also`

**Verify:** Build a small library with `data class` models and collection processing pipeline.

---

### Phase 3: Kotlin for Backend — Ktor
**Prerequisites:** Phases 1–2

1. Project setup: Gradle/Kotlin DSL, dependencies
2. Ktor: routing, request/response handling, content negotiation (JSON)
3. Serialization: `kotlinx.serialization` or Jackson
4. Dependency injection basics
5. Testing with Kotest or JUnit

**Verify:** Create a REST endpoint that returns a JSON list of resources.

---

### Phase 4: Production-Ready API
**Prerequisites:** Phase 3

1. Structured concurrency: coroutines, `suspend` functions, flows
2. Error handling: `Result` type, custom exceptions
3. Database access: Exposed ORM or JDBC with connection pooling
4. Configuration & logging
5. Middleware, authentication stubs, API documentation

**Verify:** Full CRUD API with persistence, error handling, and tests.

---

## Part 1: Learning Goals

1. Write idiomatic Kotlin with proper null safety and type discipline (no `Any?` escaping everywhere).
2. Build a REST API with Ktor using coroutines for async operations.
3. Read and reason about Kotlin standard library and common patterns without translating through Python first.

---

## Part 2: Four-Step Prompting Strategy

### Step 1 — Conceptual Understanding

**Prompt:**
> I'm proficient in Python and want to learn Kotlin. Before diving into code:
> 1. What are the key philosophical differences between Python and Kotlin?
> 2. What problems was Kotlin designed to solve?
> 3. What mental models should I adjust coming from Python?
> 4. What are common misconceptions Python developers have about Kotlin?

**Notes:** [To be filled]

---

### Step 2 — Step-by-Step Breakdown

**Prompt:**
> I want to understand null safety in Kotlin. Could you break down:
> 1. How null safety is implemented in Kotlin
> 2. How it compares to Python's approach (where anything can be `None`)
> 3. The key syntax and structures I need to understand
> 4. Common patterns and best practices

**Notes:** [To be filled]

---

### Step 3 — Guided Implementation

**Prompt:**
> I'm ready to implement my first null-safe data model in Kotlin. Could you guide me through creating a simple `User` class with nullable and non-nullable fields? Please explain each part of the syntax, especially the parts that differ from Python's dataclasses approach.

**Notes:** [To be filled]

---

### Step 4 — Understanding Verification

**Notes:** [Paste your code and verification results here]

---

## Part 3: Advanced Prompting Techniques

### Technique 1: Using Context Effectively
**Prompt:**
> I'm learning Kotlin's `sealed class` coming from Python's `Enum` and `Union` types. Could you explain sealed classes by comparing them to concepts I'm familiar with in the Python ecosystem?

**Notes:** [To be filled]

---

### Technique 2: Promoting Deep Understanding
**Prompt:**
> I've implemented this solution for a simple REST endpoint in Kotlin with Ktor:
>
> [Paste your code]
>
> Could you help me understand:
> 1. What are the performance implications?
> 2. What alternative approaches could I have taken in Kotlin?
> 3. How would this need to change if the requirements scaled 10x?
> 4. How might this implementation be different if I used Flows instead of Collections?

**Notes:** [To be filled]

---

## Part 4: Mini-Project

### Project Specification

A simple task management API with:

- `GET /tasks` — list all tasks
- `POST /tasks` — create a task
- `GET /tasks/{id}` — get a task by ID
- `PUT /tasks/{id}` — update a task
- `DELETE /tasks/{id}` — delete a task

Each task: `id`, `title`, `description`, `completed`, `createdAt`

### Key Files / Components

- `build.gradle.kts` — Gradle config with Ktor + kotlinx.serialization
- `src/main/kotlin/com/example/Application.kt` — Entry point and routing
- `src/main/kotlin/com/example/models/Task.kt` — Data model
- `src/main/kotlin/com/example/routes/TaskRoutes.kt` — Route handlers
- `src/main/kotlin/com/example/storage/TaskStore.kt` — In-memory storage
- `src/test/kotlin/com/example/TaskRoutesTest.kt` — Route tests

**Challenges coming from Python:**

- Gradle build system vs `pip`/`poetry`
- Explicit type annotations everywhere
- `suspend` functions for async (vs `async`/`await`)
- No global mutable state — need to thread dependencies
- Compilation step before running

---

## Reflection

| Question | Notes |
|---|---|
| Which prompting strategies were most effective? | [To be filled] |
| What surprised you about Kotlin? | [To be filled] |
| How did Python mental models help/hinder? | [To be filled] |
| What would you do differently next time? | [To be filled] |
| What gaps remain? | [To be filled] |

---

## Extension Ideas

- [ ] Create a cheat sheet comparing Python ↔ Kotlin concepts
- [ ] Add persistence with Exposed ORM
- [ ] Practice explaining `coroutines` in my own words
- [ ] Analyze a small open-source Ktor project
- [ ] Create a reusable prompting template for future languages
