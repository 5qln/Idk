# Cycle Essence → Strategy Documents

When the human validates the V-phase close and directs you to apply the
cycle's essence to strategy documents, this is the workflow.

## When This Happens

The human says some version of: "Yes. ... write an update both to the website
strategy branding strategy, product strategy with that because there is quite
a essence in this session."

This is a "Yes + produce" redirect: the human validated the close AND pointed
at concrete artifacts to produce.

## Workflow

1. **Locate the strategy documents.** They live in the 5qln-wiki repo:
   `/opt/data/5qln-wiki/projects/website-strategy.md`,
   `/opt/data/5qln-wiki/concepts/brand-positioning.md`,
   `/opt/data/5qln-wiki/projects/product-strategy.md` (may need creation).

2. **Read each document in full.** Don't skim — know the existing structure,
   decisions, and open questions before updating.

3. **Extract the cycle's essence.** From the trail: α (the seed), Z (what
   locked), ∇ (the direction), and any raw material the human dropped
   (articles, spontaneous language). Condense to 3-5 bullet points —
   these are the cycle's contributions to the strategy.

4. **Apply the essence to each document:**
   - **Website Strategy:** How does the cycle reframe the audience,
     the opening block, the witness layer, the CTA, propagation?
   - **Brand Positioning:** How does the cycle deepen the moat, sharpen
     the positioning statement, pivot the brand direction?
   - **Product Strategy:** How does the cycle change what the product IS,
     what gets built next, what gets stopped?

5. **Write the updates.** Add a `cycle_38_essence` (or current cycle number)
   field to the frontmatter. Integrate new sections rather than overwriting
   existing ones — the cycle deepens the strategy, it doesn't replace it.

6. **Commit and push to the wiki:**
   ```bash
   cd /opt/data/5qln-wiki
   git add projects/website-strategy.md concepts/brand-positioning.md projects/product-strategy.md
   git commit -m "Cycle N: [one-line summary of what the cycle contributed]"
   git push
   ```

7. **Report to the human** what was updated and where (repo, branch).

## Pitfalls

- **Don't overwrite:** The cycle adds a layer. Don't delete existing strategy
  decisions that weren't contradicted by the cycle.
- **Don't just paste the trail:** Translate. Strategy docs are read by humans
  who weren't in the cycle. 5QLN terminology stays in the cycle; the strategy
  docs speak in plain language.
- **The cycle essence is in the frontmatter:** The `cycle_N_essence` field
  lets future readers trace what this cycle contributed without re-reading
  the whole document.

## Example: Cycle 38

- Essence: pregnant void as actuality, void is what pool can't distribute,
  authentic question IS signature, trail IS ledger, /idk teaches language
  in practice.
- Updated: website-strategy (witness layer → trails, CTA shift), brand-positioning
  (moat deepened, describing→inhabiting pivot), product-strategy (new: trail
  as product, minimum viable cycle, signature economy).
