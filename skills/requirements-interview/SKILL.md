---
name: requirements-interview
description: Use when a request, plan or design is still fuzzy, to interview the human one question at a time until every branch of the decision tree is resolved, before anything is specified or built.
---

# Requirements interview

People rarely know every detail of what they want until they're asked. Your job is to ask
the questions they haven't thought of yet, cheaply, before code makes the answers expensive.

## Steps

1. **Map the decision tree.** From the request, list the open decisions: users, inputs,
   outputs, failure behaviour, limits, platforms, compatibility, and what "done" looks like.
   Order them so that answers to early questions remove later ones.
   **Done when:** you have a written list of open decisions, ordered by dependency.

2. **Ask one question at a time.** For each decision, ask a single question, and offer your
   recommended answer with a one-line reason, so the human can just say "yes". Offer 2–4
   concrete options where that helps.
   **Done when:** the human has answered, or said "you decide", or "defer".

3. **Probe each answer.** Push on vague words ("fast", "secure", "simple", "usually") until
   they become numbers or rules. Ask for one example and one counter-example. Ask what should
   happen when it goes wrong.
   **Done when:** the answer is specific enough to write a Given/When/Then for it.

4. **Check terms.** When the human uses a term in a new way, or two words for one thing, settle
   it and record it with the `glossary-and-decisions` skill.
   **Done when:** each new term has a glossary entry.

5. **Stop at the right time.** Stop when every decision is answered or explicitly deferred,
   not when the human seems tired. If they need a break, record the remaining questions under
   "Open questions" in the spec.
   **Done when:** the decision list is empty, or its remainder is in the spec.

## Style
- Short questions. A recommendation each time.
- Look for answers in the code, docs and ADRs before asking. Ask only what the human alone can decide.
- Summarise decisions back every 5 or so questions, so mistakes surface early.
