## SAM Workflow Instructions

This project uses the SAM micro-chunk workflow. All planning, routing, and execution
artifacts live in the `plans/` directory. Read `plans/README.md` for the full spec.

### When asked to "run the next step", "continue", or similar:

1. Read `plans/state.json` → get `next_action_id`
2. If `next_action_id` starts with `Human.*`: do NOT execute. Instead, read the
   corresponding template and prepare a briefing for the human per its instructions. Stop.
3. Read `plans/templates/registry.json` → find the action entry matching `next_action_id`
4. Read the template file at the action's `template_path` — this defines your role,
   task, constraints, and exact instructions
5. Read ALL files listed in the action's `inputs` — this is your full context
6. Execute exactly what the template instructs (bounded to that one task)
7. Update ALL files listed in `required_outputs` — this always includes `plans/STATUS.md`
8. Update `plans/state.json` with `last_action`, `next_action_id`, and `pause_type`
   as specified by the template
9. Stop. You are done when state.json is updated and all required outputs are written.
   Do not continue to the next action.

### Key files
- `plans/README.md` — full SAM system spec (vocabulary, lifecycle, pause model, etc.)
- `plans/state.json` — routing source of truth (what to do next)
- `plans/templates/registry.json` — machine-readable action catalog (inputs, outputs, gates)
- `plans/templates/*.txt` — individual action prompts
- `plans/STATUS.md` — human-readable project snapshot (updated every action)
