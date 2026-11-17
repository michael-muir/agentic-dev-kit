# Accessibility review checklist (WCAG 2.2 AA)

## Structure and semantics
- [ ] Native elements are used before ARIA (`<button>`, `<a href>`, `<label>`, `<dialog>`, platform controls). (4.1.2)
- [ ] The page or screen has one main heading, headings in order, and landmarks (`header`, `nav`, `main`). (1.3.1, 2.4.6)
- [ ] The language is set (`<html lang>`), and changes of language are marked. (3.1.1, 3.1.2)
- [ ] Lists, tables and their headers are marked up as such. (1.3.1)

## Names, roles, states
- [ ] Every interactive control has an accessible name that matches its visible label. (4.1.2, 2.5.3)
- [ ] Custom widgets expose their role and state (`aria-expanded`, `aria-selected`, `aria-checked`), following the ARIA Authoring Practices pattern. (4.1.2)
- [ ] Images have meaningful `alt` text, or `alt=""` when decorative. Icons-only buttons have a name. (1.1.1)
- [ ] Status messages are announced (`role="status"`/`aria-live`) without moving focus. (4.1.3)

## Keyboard and focus
- [ ] Everything works with the keyboard alone, with no traps. (2.1.1, 2.1.2)
- [ ] Focus order follows reading order. No positive `tabindex`. (2.4.3)
- [ ] Focus is always visible, and not hidden behind sticky headers or overlays. (2.4.7, 2.4.11)
- [ ] Dialogs move focus in, keep it inside, and return it on close. Route changes move focus to the new content.
- [ ] A skip link, or landmarks, bypass repeated blocks. (2.4.1)
- [ ] Single-key shortcuts can be turned off or remapped. (2.1.4)

## Visual
- [ ] Text contrast is ≥ 4.5:1 (large text ≥ 3:1). UI components and focus indicators are ≥ 3:1. (1.4.3, 1.4.11)
- [ ] Information isn't conveyed by colour alone. (1.4.1)
- [ ] Content reflows at 320 CSS px and 200% zoom without loss of content or function. (1.4.10, 1.4.4)
- [ ] Text spacing overrides don't break the layout. (1.4.12)
- [ ] Targets are at least 24×24 CSS px, or adequately spaced. (2.5.8)

## Motion, time, media
- [ ] `prefers-reduced-motion` (or a platform or game setting) disables non-essential animation. Nothing flashes more than 3 times a second. (2.3.1, 2.3.3)
- [ ] Time limits can be extended or turned off. Auto-moving content can be paused. (2.2.1, 2.2.2)
- [ ] Video has captions. Audio-only content has transcripts. Games offer subtitles with size and background options. (1.2.2, 1.2.1)

## Forms and errors
- [ ] Inputs have visible labels, and programmatic association. Required fields are indicated in text. (3.3.2, 1.3.1)
- [ ] Errors are identified in text, linked to the field, and announced, with how to fix them. (3.3.1, 3.3.3)
- [ ] Autocomplete attributes are set for personal-data fields. (1.3.5)
- [ ] Authentication doesn't rely on a cognitive test alone (puzzles, transcription). (3.3.8)

## Tooling
- [ ] The automated checks pass: the kit's `accessibility-expert:markup-basics`, and axe/pa11y on rendered pages, where configured.
- [ ] Linters are enabled where the stack has them: `eslint-plugin-jsx-a11y` (React), `eslint-plugin-vuejs-accessibility` (Vue), and the platform accessibility inspector (Accessibility Insights for Windows, Xcode, Android).
