# Motion And Interaction

Motion is feedback, orientation, or continuity—not decoration.

- Select timing and easing by the event: enter/reveal generally decelerates, exit may accelerate, direct manipulation follows the pointer, and state confirmation must not wait for a long animation.
- Make interactions interruptible. A rapid second action leaves focus, semantic state, and visual state correct.
- Animate cheap properties where possible and avoid continuous layout-heavy effects. Pause nonessential work when hidden or offscreen.
- Under `prefers-reduced-motion`, show a designed stable state instead of hiding essential information or controls.
- Ensure hover states have focus and touch equivalents. Tooltips must not be the only way to learn a control's function.

Use `templates/Component-Contract.md` to record trigger, state transition, duration, cancellation, focus, and reduced-motion behavior.
