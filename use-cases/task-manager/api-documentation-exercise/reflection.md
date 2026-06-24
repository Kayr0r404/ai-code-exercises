# Reflection — API Documentation Exercise

### Which parts of the API were most challenging to document?

The query parameter filtering was the trickiest part. The list endpoint has seven optional parameters that interact in subtle ways — for example, `minPrice` and `maxPrice` together build a range filter, while `inStock` sets a completely different kind of filter on `stockQuantity`. Documenting each parameter individually was straightforward, but explaining how they compose required real care. I also found the error handling for the single-product endpoint interesting: the code catches both expected (404) and unexpected (CastError for invalid ObjectId format) errors, and I had to distinguish between "bad request" (400) and "not found" (404) in the docs to help developers debug their integration.

### How did I adjust my prompts to get better results?

Initially I tried to document both endpoints in a single pass, but the output was too dense. Splitting the work — one prompt per endpoint — gave much clearer per-endpoint documentation. For the OpenAPI spec, I found that starting with a skeleton (info + servers) and then filling in each path and schema iteratively produced a more consistent spec than asking for everything at once. For the developer guide, the biggest improvement came from explicitly stating the target audience ("frontend and mobile developers") and asking for code examples in multiple languages — the prompt generated much more practical, ready-to-use snippets.

### Which documentation format did I find most effective for this API?

Each format serves a different purpose:

- **Markdown documentation** is best for human readability and onboarding. The table of query parameters is instantly scannable, and the example request/response pairs give developers confidence they're using the API correctly.
- **OpenAPI/Swagger** is best for tooling integration. It enables auto-generated client libraries, interactive docs (Swagger UI), and contract testing. The schema definitions for `Product`, `Pagination`, and `Error` are reusable across endpoints.
- **Developer guide** is best for reducing support questions. The code snippets in cURL, JavaScript, Python, and Node.js cover the three most common integration patterns, and the defensive coding and best practices sections answer questions before they're asked.

For this particular API, the OpenAPI spec is the most valuable long-term asset because it can drive documentation generation, client SDKs, and API testing. But the Markdown docs are what a developer will actually read first.

### How would I incorporate this approach into my development workflow?

I would treat API documentation as a design tool, not a post-implementation chore:

1. **Write the OpenAPI spec first** (design-first approach) — share it with frontend and mobile teams for feedback before writing any route handlers
2. **Generate Markdown docs automatically** from the OpenAPI spec using a tool like Redoc or Swagger UI — this keeps docs in sync with the spec
3. **Write the developer guide after the first round of QA** — real developer feedback reveals which parts of the API are confusing and need extra explanation
4. **Keep code examples in CI** — if the API changes, regenerate or update the snippets; broken examples erode trust

The three-prompt structure (endpoint docs → OpenAPI conversion → usage guide) mirrors this workflow nicely and forces you to think about each layer of documentation independently.
