---
name: accessibility-audit
description: Use when reviewing or designing any user interface (web, desktop, mobile or game UI), to audit it against WCAG 2.2 AA with automated checks, a keyboard-only pass, a screen-reader pass and visual checks, producing findings tied to success criteria.
---

# Accessibility audit

Automated tools find a minority of accessibility problems. The manual passes below are
what make an audit real.

## Steps
1. **Scope it.** List the screens, flows and components the change touches, the platforms
   (browser plus screen reader, desktop OS, mobile, game platform), and the target (WCAG 2.2
   AA unless the spec says otherwise).
   **Done when:** each flow has a platform and assistive-tech pairing, e.g. Chrome + NVDA,
   Safari + VoiceOver, or Windows + Narrator.
2. **Automated checks.** Run the gate's `accessibility-expert:markup-basics`, and axe-core
   (browser extension, `@axe-core/playwright`, or pa11y-ci) on each rendered screen, or the
   platform's checker (Accessibility Insights, Xcode Accessibility Inspector, Android
   Accessibility Scanner).
   **Done when:** each reported issue is a finding, or is dismissed with a reason.
3. **Keyboard pass.** Unplug the mouse. Complete each flow with Tab, Shift+Tab, Enter, Space,
   the arrow keys and Escape. Watch for a visible focus ring, a logical order, no traps, focus
   moving into and out of dialogs, and focus landing somewhere sensible after actions and route changes.
   **Done when:** each flow is marked completed, or the step where it fails is recorded.
4. **Screen-reader pass.** With the paired screen reader, navigate by headings, landmarks
   and form controls, then complete each flow. Check that every control announces its name,
   role and state, that errors and status messages are announced, and that images and icons
   make sense.
   **Done when:** each flow has an announced-as-expected or a failure record.
5. **Visual pass.** Check contrast with a contrast checker, including focus rings and states.
   Zoom to 200% and reflow at 320 px width. Apply text-spacing overrides. Turn on reduced
   motion and high-contrast/forced-colours modes. Check that colour isn't the only signal.
   **Done when:** each check is marked pass or fail, with a screenshot path for each failure.
6. **File the findings** with the WCAG criterion, the user impact (who is blocked and how),
   the steps to reproduce, and a direction for the fix (preferring native elements over ARIA).
   Severity: a blocker for a task is `critical`, a serious barrier is `major`, an annoyance is `minor`.

## Game and engine UI
For Unreal UMG, Unity UI or custom engines, also check:
- remappable controls, and full controller and keyboard navigation of every menu;
- subtitle size, background and speaker labels;
- colour-blind-safe palettes, or alternate modes;
- screen-reader or text-to-speech support where the platform provides it;
- options to turn off camera shake, flashes and motion blur.
