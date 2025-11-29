"""
Quick test for the Export as JSON feature in DFA Builder
"""
from PyQt5.QtWidgets import QApplication
import sys
from dfa_builder import DFABuilderDialog

def test_export_feature():
    """Test the export feature."""
    app = QApplication(sys.argv)
    
    # Create builder dialog
    dialog = DFABuilderDialog()
    
    print("✓ DFA Builder opened successfully")
    print("✓ Export as JSON button should be visible")
    print("\nTo test:")
    print("1. Add states (e.g., q0, q1)")
    print("2. Add alphabet symbols (e.g., a, b)")
    print("3. Add transitions")
    print("4. Set start state")
    print("5. Add final states")
    print("6. Click '💾 Export as JSON' button")
    print("7. Choose filename and save")
    print("8. Verify JSON file is created")
    
    dialog.exec_()
    app.quit()

if __name__ == '__main__':
    test_export_feature()
