# Getting Started with DFA Simulator

## Welcome! 👋

This guide will help you get the DFA Simulator up and running in just a few minutes.

---

## Prerequisites

Before you begin, make sure you have:
- ✅ **Git** installed ([Download Git](https://git-scm.com/downloads))
- ✅ **Python 3.7+** installed ([Download Python](https://www.python.org/downloads/))
- ✅ **Terminal/Command Prompt** access

---

## Step 1: Clone the Repository

Open your terminal and run:

```bash
# Clone the repository
git clone https://github.com/yourusername/DFASimulator.git

# Navigate to the project folder
cd DFASimulator
```

**Alternative**: Download ZIP
- Go to the repository page
- Click "Code" → "Download ZIP"
- Extract the ZIP file
- Open terminal in the extracted folder

---

## Step 2: Verify Python

Check your Python version:

```bash
python --version
```

You should see something like `Python 3.7.0` or higher.

**If Python is not found:**
- Windows: Add Python to PATH during installation
- macOS: Use `python3` instead of `python`
- Linux: Install with `sudo apt install python3`

---

## Step 3: Choose Your Setup

### Option A: Core Only (No GUI)

**No installation needed!** Just run:

```bash
python dfa.py
```

This gives you:
- ✅ DFA creation and validation
- ✅ String acceptance testing
- ✅ Step-by-step execution traces
- ✅ JSON import/export
- ❌ No graphical interface

---

### Option B: Full Features (With GUI) - Recommended

**Install GUI packages:**

```bash
pip install PyQt5 matplotlib networkx
```

Or use the requirements file:

```bash
pip install -r requirements.txt
```

This gives you:
- ✅ Everything from Core
- ✅ Interactive graphical interface
- ✅ Visual graph rendering
- ✅ Step-by-step debugger with highlighting
- ✅ Manual DFA creation

---

## Step 4: Run the Application

### Interactive Debugger (Recommended)

```bash
python interactive_debugger.py
```

**What you'll see:**
- A window with controls on the left
- Graph visualization on the right
- Buttons to load, create, or clear DFAs

### Basic Visualizer

```bash
python dfa_visualizer.py
```

**What you'll see:**
- Similar interface
- Focus on testing and visualization

### Test Core Functionality

```bash
python dfa.py
```

**What you'll see:**
- Terminal output showing test results
- Validates core functionality

---

## Step 5: Try Your First DFA

### Method 1: Load an Example

1. Click **"📁 Load"** button
2. Select `even_a_dfa.json`
3. DFA loads and displays in graph

### Method 2: Create Manually

1. Click **"✏️ Create"** button
2. Follow the step-by-step builder:
   - Add states: `q0`, `q1`
   - Add symbols: `a`, `b`
   - Add transitions
   - Set start and final states
3. Click **"✓ Create DFA"**

---

## Step 6: Test a String

1. Enter a test string (e.g., `aba`)
2. Click **"▶ Run / Reset"**
3. Click **"⏭ Next Step"** to step through execution
4. Watch the visualization:
   - **Gold circle** = current state
   - **Red arrow** = current transition
   - **Green** = start state
   - **Double circle** = final state

---

## Quick Reference

### Common Commands

```bash
# Run interactive debugger
python interactive_debugger.py

# Run basic visualizer
python dfa_visualizer.py

# Test core functionality
python dfa.py

# Run examples
python debugger_demo.py
python complete_workflow_demo.py
```

### Example DFAs Included

| File | Description |
|------|-------------|
| `even_a_dfa.json` | Accepts strings with even number of 'a's |
| `ends_with_ab.json` | Accepts strings ending with "ab" |
| `divisible_by_3.json` | Binary numbers divisible by 3 |
| `odd_b_dfa.json` | Accepts strings with odd number of 'b's |

---

## Troubleshooting

### "No module named 'PyQt5'"

**Solution:**
```bash
pip install PyQt5
```

### "python: command not found"

**Solution:**
- Try `python3` instead of `python`
- Or reinstall Python and add to PATH

### "pip: command not found"

**Solution:**
```bash
python -m pip install PyQt5 matplotlib networkx
```

### GUI doesn't open

**Solution:**
1. Check if packages are installed: `pip list`
2. Try reinstalling: `pip install --force-reinstall PyQt5`
3. Use core functionality: `python dfa.py`

### Permission errors

**Solution:**
```bash
pip install --user PyQt5 matplotlib networkx
```

---

## Next Steps

### Learn More

1. **[Quick Start Guide](docs/QUICKSTART.md)** - 5-minute tutorial
2. **[User Guide](docs/usage/USER_GUIDE.md)** - Complete instructions
3. **[Examples](docs/usage/EXAMPLES.md)** - Usage examples
4. **[FAQ](docs/usage/FAQ.md)** - Common questions

### Try These

- Load different example DFAs
- Create your own DFA manually
- Test various strings
- Use step-by-step debugging
- Export DFAs to JSON

### Explore Features

- **Auto-play mode** - Automatic stepping
- **Previous button** - Go back in execution
- **Manual creation** - Build DFAs visually
- **JSON import/export** - Save and share DFAs

---

## Getting Help

If you need assistance:

1. **Check Documentation**
   - [Installation Guide](docs/setup/INSTALLATION.md)
   - [User Guide](docs/usage/USER_GUIDE.md)
   - [FAQ](docs/usage/FAQ.md)

2. **Try Examples**
   - Run demo files
   - Load example DFAs
   - Follow tutorials

3. **Read Error Messages**
   - They're descriptive and helpful
   - Point to the specific issue

4. **Start Simple**
   - Use example DFAs first
   - Test with short strings
   - Build complexity gradually

---

## Success Checklist

- [ ] Repository cloned
- [ ] Python 3.7+ installed
- [ ] Dependencies installed (for GUI)
- [ ] Application runs successfully
- [ ] Can load example DFA
- [ ] Can test strings
- [ ] Can step through execution
- [ ] Understand basic controls

---

## What's Next?

You're all set! Here are some suggestions:

1. **Explore Examples**
   - Load each example DFA
   - Test different strings
   - Understand the patterns

2. **Create Your Own**
   - Use the manual builder
   - Start with 2-3 states
   - Test thoroughly

3. **Learn DFA Theory**
   - Read the documentation
   - Try the examples
   - Experiment with designs

4. **Share Your Work**
   - Export DFAs to JSON
   - Share with others
   - Collaborate on designs

---

## Quick Tips

💡 **Tip 1**: Start with `even_a_dfa.json` - it's simple and clear

💡 **Tip 2**: Use step-by-step mode to understand execution

💡 **Tip 3**: The manual builder is great for learning

💡 **Tip 4**: Test edge cases (empty string, single symbols)

💡 **Tip 5**: Read the visual legend in the control panel

---

## Resources

- **[Main README](README.md)** - Project overview
- **[Documentation Index](docs/README.md)** - All documentation
- **[Installation Guide](docs/setup/INSTALLATION.md)** - Detailed setup
- **[User Guide](docs/usage/USER_GUIDE.md)** - Complete instructions

---

**You're ready to start exploring DFAs! Have fun! 🎉**
