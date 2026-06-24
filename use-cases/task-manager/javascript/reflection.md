# Reflection — README and User Guide Documentation Exercise

### Which aspects of the project were most challenging to document?

The most challenging aspect was accurately describing the CLI interface — specifically capturing all the command options, their defaults, and the exact output format. The `list` command, for example, has three different filter flags that can be combined in various ways, and documenting every combination required careful reading of the source code. Another challenge was deciding how much detail to include about the internal architecture (three-layer separation) without overwhelming a new user. The status flow (`todo → in_progress → review → done`) was straightforward, but explaining when `completedAt` is automatically set required tracing through the code.

### How did I adjust my approach to get better results?

Initially, I tried to pull feature descriptions from the PDF example, but that described a different tool (with GitHub integration, time tracking, email notifications). I realized I needed to work directly from the source code — reading `cli.js`, `app.js`, `models.js`, and `storage.js` to extract the exact command signatures, option names, and behavior. For the FAQ, I focused on the questions a first-time terminal user would actually ask (date format, data location, persistence) rather than hypothetical edge cases. The step-by-step guide benefited from running the commands mentally in sequence — each step builds on the previous one.

### What did I learn about document structure and organization?

The three document types serve very different audiences, even for the same project:

1. **README** — A reference document. Needs a command table, architecture diagram, and quick start. It should be skimmable — users come here to find specific information fast.
2. **Step-by-step guide** — A tutorial. Must be linear, each step producing visible output. The user should feel progress. Screenshots or example output are essential for confidence.
3. **FAQ** — A troubleshooting document. Organized by user intent ("How do I...") rather than by feature. Covers installation, common errors, and conceptual questions.

The biggest structural lesson was that the README should never try to be a tutorial and vice versa. Mixing them produces a document that's neither skimmable nor walkable.

### How would I incorporate this approach into my development workflow?

I would adopt documentation as a parallel track to development:
1. Write the README first (even before code) to clarify the API surface and UX
2. Write the step-by-step guide during QA to verify the intended workflow makes sense
3. Publish the FAQ after the first batch of user feedback, addressing real confusion points

Prompt engineering for documentation is valuable because it forces you to think about what information each audience needs and in what format. I'd use different prompts for each document type rather than one generic "document this" prompt.

---

## Submitted files

| File | Description |
|------|-------------|
| `exercise5-readme-documentation.md` | Comprehensive README generated using Prompt 1 |
| `step-by-step-guide.md` | Step-by-step guide created using Prompt 2 |
| `faq.md` | FAQ document created using Prompt 3 |
| `reflection.md` | This reflection on the documentation process |
