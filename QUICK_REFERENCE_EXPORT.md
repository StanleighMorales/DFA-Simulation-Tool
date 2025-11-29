# Quick Reference: Export from Builder

## One-Line Summary
**Save your DFA to JSON while building it, without closing the builder dialog.**

---

## Quick Start

```
1. Open builder: Click "✏️ Create"
2. Build your DFA
3. Click "💾 Export as JSON"
4. Choose filename
5. Done! Keep editing or finish.
```

---

## Button Layout

```
Main Window:
┌──────────────────────────────────────┐
│  📁 Load      ✏️ Create              │  ← Click "Create"
│  📝 Edit      💾 Export              │
│  🗑️ Clear                            │
└──────────────────────────────────────┘

Builder Dialog:
┌─────────────────────────────────────────┐
│  💾 Export as JSON  │  ✓ Create DFA  │  Cancel  │
└─────────────────────────────────────────┘
         ↑
    Click here to export!
```

---

## What It Does

| Action | Result |
|--------|--------|
| Click "💾 Export as JSON" | Opens file dialog |
| Choose filename | Saves DFA to JSON |
| Dialog behavior | Stays open |
| Can continue editing | ✅ Yes |
| Can export again | ✅ Yes |

---

## Validation Checks

✅ **Must have**: States, alphabet, start state  
⚠️ **Warns if missing**: Final states, complete transitions  
👍 **Your choice**: Export anyway or fix first

---

## Common Uses

| Scenario | Action |
|----------|--------|
| Save progress | Export as "draft.json" |
| Create backup | Export as "backup.json" |
| Share work | Export as "homework.json" |
| Version control | Export as "v1.json", "v2.json" |

---

## Export vs Create DFA

| Feature | Export | Create DFA |
|---------|--------|------------|
| Saves to file | ✅ | ❌ |
| Closes dialog | ❌ | ✅ |
| Loads into app | ❌ | ✅ |
| Continue editing | ✅ | ❌ |

**Tip**: Export to save, Create DFA to finish!

---

## Keyboard Shortcuts (Future)

Coming soon:
- `Ctrl+S` - Quick export
- `Ctrl+Shift+S` - Export as

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| Button disabled | Not implemented (it's always enabled) |
| "Add at least one state" | Add states first |
| "Add at least one symbol" | Add alphabet symbols first |
| "Set a start state" | Set start state first |
| File not created | Check permissions, disk space |

---

## File Format

Standard DFA JSON:
```json
{
  "states": ["q0", "q1"],
  "alphabet": ["a", "b"],
  "transitions": {
    "q0": {"a": "q1", "b": "q0"},
    "q1": {"a": "q1", "b": "q0"}
  },
  "start_state": "q0",
  "final_states": ["q1"]
}
```

---

## Tips

💡 **Export early, export often**  
💡 **Use descriptive filenames**  
💡 **Create backups before big changes**  
💡 **Version your exports (v1, v2, v3)**  
💡 **Test after exporting (click Create DFA)**

---

## Documentation

- 📖 Full guide: `docs/usage/EXPORT_FROM_BUILDER.md`
- 📖 Manual creation: `docs/usage/MANUAL_DFA_CREATION.md`
- 📖 Technical: `docs/updates/EXPORT_FROM_BUILDER_FEATURE.md`

---

## Status

✅ Ready to use!

**Happy DFA building!** 💾
