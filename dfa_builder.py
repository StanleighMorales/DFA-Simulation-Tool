"""
DFA Builder - GUI for manually creating DFAs

This module provides a graphical user interface for creating and editing
Deterministic Finite Automata (DFAs) without writing JSON files manually.

Key Features:
- Step-by-step DFA construction (states, alphabet, transitions, etc.)
- Visual feedback and validation
- Export to JSON while continuing to edit
- Edit existing DFAs
- Comprehensive error checking

Classes:
    DFABuilderDialog: Main dialog for building/editing DFAs

Usage:
    from dfa_builder import DFABuilderDialog
    
    # Create new DFA
    builder = DFABuilderDialog()
    if builder.exec_() == QDialog.Accepted:
        dfa = builder.get_dfa()
    
    # Edit existing DFA
    builder = DFABuilderDialog(existing_dfa=my_dfa)
    if builder.exec_() == QDialog.Accepted:
        dfa = builder.get_dfa()
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QGroupBox, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QFileDialog
)
from PyQt5.QtCore import Qt
from dfa import DFA


class DFABuilderDialog(QDialog):
    """
    Dialog for manually creating or editing a Deterministic Finite Automaton (DFA).
    
    This dialog provides a step-by-step interface for building DFAs:
    1. Define states (Q)
    2. Define alphabet (Σ)
    3. Define transitions (δ)
    4. Set start state (q₀)
    5. Set final/accept states (F)
    
    The dialog supports two modes:
    - Create mode: Build a new DFA from scratch
    - Edit mode: Modify an existing DFA
    
    Key Methods:
        - export_dfa(): Export DFA to JSON without closing dialog
        - create_dfa(): Create DFA and close dialog (loads into app)
        - get_dfa(): Retrieve the created DFA object
        - load_existing_dfa(): Load existing DFA for editing
    
    Attributes:
        states (list): List of state names (strings)
        alphabet (list): List of alphabet symbols (strings)
        transitions (dict): Transition function as {(state, symbol): next_state}
        start_state (str): Name of the start state
        final_states (list): List of final/accept state names
    
    Example:
        # Create new DFA
        builder = DFABuilderDialog()
        if builder.exec_() == QDialog.Accepted:
            dfa = builder.get_dfa()
            # Use dfa...
        
        # Edit existing DFA
        builder = DFABuilderDialog(existing_dfa=my_dfa)
        if builder.exec_() == QDialog.Accepted:
            modified_dfa = builder.get_dfa()
    """
    
    def __init__(self, parent=None, existing_dfa=None):
        """
        Initialize the DFA Builder Dialog.
        
        Args:
            parent (QWidget, optional): Parent widget. Defaults to None.
            existing_dfa (DFA, optional): Existing DFA to edit. If provided,
                the dialog will be in "Edit" mode and pre-populated with the
                DFA's components. If None, dialog is in "Create" mode.
        
        The dialog is modal, meaning it blocks interaction with other windows
        until it is closed.
        """
        super().__init__(parent)
        
        # Set window title based on mode (Create vs Edit)
        self.setWindowTitle('Edit DFA' if existing_dfa else 'Create DFA Manually')
        
        # Set dialog size and position
        self.setGeometry(150, 150, 800, 600)  # x, y, width, height
        
        # Make dialog modal (blocks other windows)
        self.setModal(True)
        
        # ============================================================
        # Initialize DFA Components
        # ============================================================
        # These store the DFA's 5-tuple components:
        # DFA = (Q, Σ, δ, q₀, F)
        
        self.states = []          # Q: Set of states (stored as list for ordering)
        self.alphabet = []        # Σ: Alphabet (input symbols)
        self.transitions = {}     # δ: Transition function {(state, symbol): next_state}
        self.start_state = None   # q₀: Start state
        self.final_states = []    # F: Set of final/accept states
        
        # ============================================================
        # Build User Interface
        # ============================================================
        # Create all GUI components (buttons, lists, tables, etc.)
        self.init_ui()
        
        # ============================================================
        # Load Existing DFA (if in Edit mode)
        # ============================================================
        # If an existing DFA was provided, populate the dialog with its data
        if existing_dfa:
            self.load_existing_dfa(existing_dfa)
    
    def init_ui(self):
        """
        Initialize the user interface for the DFA Builder.
        
        This method creates all GUI components organized in a step-by-step layout:
        
        Layout Structure:
        ┌─────────────────────────────────────────┐
        │           Build Your DFA                │  ← Title
        ├─────────────────────────────────────────┤
        │  Instructions...                        │  ← Help text
        ├──────────────────┬──────────────────────┤
        │ 1. States        │ 3. Transitions       │  ← Two columns
        │ 2. Alphabet      │ 4. Start & Final     │
        ├──────────────────┴──────────────────────┤
        │  [Export] [Create DFA] [Cancel]         │  ← Action buttons
        └─────────────────────────────────────────┘
        
        Components Created:
        - Title label
        - Instructions label
        - States section (list + add/remove buttons)
        - Alphabet section (list + add/remove buttons)
        - Transitions section (table + add/remove buttons)
        - Start & Final states section (combos + lists)
        - Action buttons (Export, Create DFA, Cancel)
        
        All components are connected to their respective handler methods.
        """
        
        # ============================================================
        # Main Layout Setup
        # ============================================================
        # Vertical layout for the entire dialog
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # ============================================================
        # Title Section
        # ============================================================
        # Large, bold title at the top of the dialog
        title = QLabel('Build Your DFA')
        title.setStyleSheet('font-size: 18px; font-weight: bold; padding: 10px;')
        title.setAlignment(Qt.AlignCenter)  # Center the title
        main_layout.addWidget(title)
        
        # ============================================================
        # Instructions Section
        # ============================================================
        # Brief instructions to guide the user
        # Light blue background (#e3f2fd) makes it stand out
        instructions = QLabel(
            'Create a DFA by defining states, alphabet, transitions, start state, and final states.'
        )
        instructions.setWordWrap(True)  # Allow text to wrap to multiple lines
        instructions.setStyleSheet('padding: 5px; background-color: #e3f2fd; border-radius: 3px;')
        main_layout.addWidget(instructions)
        
        # ============================================================
        # Content Layout (Two Columns)
        # ============================================================
        # Horizontal layout to split content into left and right columns
        # Left: States and Alphabet
        # Right: Transitions and Start/Final States
        content_layout = QHBoxLayout()
        main_layout.addLayout(content_layout)
        
        # Left column - States and Alphabet
        left_column = QVBoxLayout()
        content_layout.addLayout(left_column)
        
        # States section
        states_group = QGroupBox("1. States")
        states_layout = QVBoxLayout()
        
        state_input_layout = QHBoxLayout()
        self.state_input = QLineEdit()
        self.state_input.setPlaceholderText('Enter state name (e.g., q0)')
        state_input_layout.addWidget(self.state_input)
        
        add_state_btn = QPushButton('Add State')
        add_state_btn.clicked.connect(self.add_state)
        state_input_layout.addWidget(add_state_btn)
        
        states_layout.addLayout(state_input_layout)
        
        self.states_list = QListWidget()
        self.states_list.setMaximumHeight(150)
        states_layout.addWidget(self.states_list)
        
        remove_state_btn = QPushButton('Remove Selected')
        remove_state_btn.clicked.connect(self.remove_state)
        states_layout.addWidget(remove_state_btn)
        
        states_group.setLayout(states_layout)
        left_column.addWidget(states_group)
        
        # Alphabet section
        alphabet_group = QGroupBox("2. Alphabet")
        alphabet_layout = QVBoxLayout()
        
        alphabet_input_layout = QHBoxLayout()
        self.alphabet_input = QLineEdit()
        self.alphabet_input.setPlaceholderText('Enter symbol (e.g., a, 0, 1)')
        alphabet_input_layout.addWidget(self.alphabet_input)
        
        add_symbol_btn = QPushButton('Add Symbol')
        add_symbol_btn.clicked.connect(self.add_symbol)
        alphabet_input_layout.addWidget(add_symbol_btn)
        
        alphabet_layout.addLayout(alphabet_input_layout)
        
        self.alphabet_list = QListWidget()
        self.alphabet_list.setMaximumHeight(150)
        alphabet_layout.addWidget(self.alphabet_list)
        
        remove_symbol_btn = QPushButton('Remove Selected')
        remove_symbol_btn.clicked.connect(self.remove_symbol)
        alphabet_layout.addWidget(remove_symbol_btn)
        
        alphabet_group.setLayout(alphabet_layout)
        left_column.addWidget(alphabet_group)
        
        # Right column - Transitions and Final States
        right_column = QVBoxLayout()
        content_layout.addLayout(right_column)
        
        # Transitions section
        transitions_group = QGroupBox("3. Transitions")
        transitions_layout = QVBoxLayout()
        
        trans_input_layout = QVBoxLayout()
        
        from_layout = QHBoxLayout()
        from_layout.addWidget(QLabel('From State:'))
        self.from_state_combo = QComboBox()
        from_layout.addWidget(self.from_state_combo)
        trans_input_layout.addLayout(from_layout)
        
        symbol_layout = QHBoxLayout()
        symbol_layout.addWidget(QLabel('On Symbol:'))
        self.symbol_combo = QComboBox()
        symbol_layout.addWidget(self.symbol_combo)
        trans_input_layout.addLayout(symbol_layout)
        
        to_layout = QHBoxLayout()
        to_layout.addWidget(QLabel('To State:'))
        self.to_state_combo = QComboBox()
        to_layout.addWidget(self.to_state_combo)
        trans_input_layout.addLayout(to_layout)
        
        transitions_layout.addLayout(trans_input_layout)
        
        add_transition_btn = QPushButton('Add Transition')
        add_transition_btn.clicked.connect(self.add_transition)
        transitions_layout.addWidget(add_transition_btn)
        
        self.transitions_table = QTableWidget()
        self.transitions_table.setColumnCount(3)
        self.transitions_table.setHorizontalHeaderLabels(['From', 'Symbol', 'To'])
        self.transitions_table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)
        self.transitions_table.setMaximumHeight(200)
        transitions_layout.addWidget(self.transitions_table)
        
        remove_transition_btn = QPushButton('Remove Selected')
        remove_transition_btn.clicked.connect(self.remove_transition)
        transitions_layout.addWidget(remove_transition_btn)
        
        transitions_group.setLayout(transitions_layout)
        right_column.addWidget(transitions_group)
        
        # Start and Final States section
        special_group = QGroupBox("4. Start & Final States")
        special_layout = QVBoxLayout()
        
        start_layout = QHBoxLayout()
        start_layout.addWidget(QLabel('Start State:'))
        self.start_state_combo = QComboBox()
        start_layout.addWidget(self.start_state_combo)
        set_start_btn = QPushButton('Set')
        set_start_btn.clicked.connect(self.set_start_state)
        start_layout.addWidget(set_start_btn)
        special_layout.addLayout(start_layout)
        
        self.start_state_label = QLabel('Not set')
        self.start_state_label.setStyleSheet('padding: 5px; background-color: #fff3e0;')
        special_layout.addWidget(self.start_state_label)
        
        final_layout = QHBoxLayout()
        final_layout.addWidget(QLabel('Final States:'))
        self.final_state_combo = QComboBox()
        final_layout.addWidget(self.final_state_combo)
        add_final_btn = QPushButton('Add')
        add_final_btn.clicked.connect(self.add_final_state)
        final_layout.addWidget(add_final_btn)
        special_layout.addLayout(final_layout)
        
        self.final_states_list = QListWidget()
        self.final_states_list.setMaximumHeight(80)
        special_layout.addWidget(self.final_states_list)
        
        remove_final_btn = QPushButton('Remove Selected')
        remove_final_btn.clicked.connect(self.remove_final_state)
        special_layout.addWidget(remove_final_btn)
        
        special_group.setLayout(special_layout)
        right_column.addWidget(special_group)
        
        # ============================================================
        # Bottom Action Buttons
        # ============================================================
        # Three buttons for different actions:
        # 1. Export as JSON - Save to file, keep dialog open
        # 2. Create DFA - Finish and load into application
        # 3. Cancel - Close without creating DFA
        
        button_layout = QHBoxLayout()
        
        # ------------------------------------------------------------
        # Export Button (NEW FEATURE)
        # ------------------------------------------------------------
        # Allows users to save their DFA to a JSON file while continuing
        # to work in the builder. This is useful for:
        # - Saving work in progress
        # - Creating backups before major changes
        # - Exporting multiple versions
        # - Sharing DFAs with others
        #
        # Key differences from "Create DFA":
        # - Does NOT close the dialog
        # - Does NOT load DFA into the application
        # - Can be used multiple times
        # - Validates before export but allows incomplete DFAs with warnings
        
        export_btn = QPushButton('💾 Export as JSON')
        
        # Purple color (#9C27B0) distinguishes it from other buttons
        # White text for contrast, 10px padding for comfortable clicking
        export_btn.setStyleSheet('background-color: #9C27B0; color: white; padding: 10px;')
        
        # Connect to export_dfa method (defined below)
        export_btn.clicked.connect(self.export_dfa)
        
        # Add to button layout
        button_layout.addWidget(export_btn)
        
        # ------------------------------------------------------------
        # Create DFA Button (Primary Action)
        # ------------------------------------------------------------
        # This is the main action button that:
        # - Validates the DFA
        # - Creates the DFA object
        # - Closes the dialog
        # - Returns the DFA to the calling application
        #
        # Use this when you're done building and want to use the DFA
        
        create_btn = QPushButton('✓ Create DFA')
        
        # Green color (#4CAF50) indicates primary/success action
        # Bold font emphasizes this is the main action
        create_btn.setStyleSheet('background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;')
        
        # Connect to create_dfa method
        create_btn.clicked.connect(self.create_dfa)
        
        # Add to button layout
        button_layout.addWidget(create_btn)
        
        # ------------------------------------------------------------
        # Cancel Button
        # ------------------------------------------------------------
        # Closes the dialog without creating or exporting anything
        # Uses default styling (no custom colors)
        
        cancel_btn = QPushButton('Cancel')
        
        # reject() is a QDialog method that closes with "rejected" status
        # The calling code can check if dialog was accepted or rejected
        cancel_btn.clicked.connect(self.reject)
        
        # Add to button layout
        button_layout.addWidget(cancel_btn)
        
        # Add button layout to main layout
        main_layout.addLayout(button_layout)
    
    def add_state(self):
        """Add a state to the DFA."""
        state = self.state_input.text().strip()
        if not state:
            QMessageBox.warning(self, 'Warning', 'Please enter a state name.')
            return
        
        if state in self.states:
            QMessageBox.warning(self, 'Warning', f'State "{state}" already exists.')
            return
        
        self.states.append(state)
        self.states_list.addItem(state)
        self.state_input.clear()
        
        # Update combo boxes
        self.update_combos()
    
    def remove_state(self):
        """Remove selected state."""
        current_item = self.states_list.currentItem()
        if not current_item:
            return
        
        state = current_item.text()
        self.states.remove(state)
        self.states_list.takeItem(self.states_list.currentRow())
        
        # Remove related transitions
        to_remove = [k for k in self.transitions.keys() if k[0] == state]
        for k in to_remove:
            del self.transitions[k]
        
        # Update table
        self.update_transitions_table()
        self.update_combos()
    
    def add_symbol(self):
        """Add a symbol to the alphabet."""
        symbol = self.alphabet_input.text().strip()
        if not symbol:
            QMessageBox.warning(self, 'Warning', 'Please enter a symbol.')
            return
        
        if symbol in self.alphabet:
            QMessageBox.warning(self, 'Warning', f'Symbol "{symbol}" already exists.')
            return
        
        self.alphabet.append(symbol)
        self.alphabet_list.addItem(symbol)
        self.alphabet_input.clear()
        
        # Update combo boxes
        self.update_combos()
    
    def remove_symbol(self):
        """Remove selected symbol."""
        current_item = self.alphabet_list.currentItem()
        if not current_item:
            return
        
        symbol = current_item.text()
        self.alphabet.remove(symbol)
        self.alphabet_list.takeItem(self.alphabet_list.currentRow())
        
        # Remove related transitions
        to_remove = [k for k in self.transitions.keys() if k[1] == symbol]
        for k in to_remove:
            del self.transitions[k]
        
        # Update table
        self.update_transitions_table()
        self.update_combos()
    
    def add_transition(self):
        """Add a transition."""
        from_state = self.from_state_combo.currentText()
        symbol = self.symbol_combo.currentText()
        to_state = self.to_state_combo.currentText()
        
        if not from_state or not symbol or not to_state:
            QMessageBox.warning(self, 'Warning', 'Please select from state, symbol, and to state.')
            return
        
        key = (from_state, symbol)
        if key in self.transitions:
            reply = QMessageBox.question(
                self, 'Overwrite?',
                f'Transition from {from_state} on {symbol} already exists. Overwrite?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        self.transitions[key] = to_state
        self.update_transitions_table()
    
    def remove_transition(self):
        """Remove selected transition."""
        current_row = self.transitions_table.currentRow()
        if current_row < 0:
            return
        
        from_state = self.transitions_table.item(current_row, 0).text()
        symbol = self.transitions_table.item(current_row, 1).text()
        
        key = (from_state, symbol)
        if key in self.transitions:
            del self.transitions[key]
        
        self.update_transitions_table()
    
    def set_start_state(self):
        """Set the start state."""
        state = self.start_state_combo.currentText()
        if not state:
            QMessageBox.warning(self, 'Warning', 'Please select a state.')
            return
        
        self.start_state = state
        self.start_state_label.setText(f'Start State: {state}')
        self.start_state_label.setStyleSheet('padding: 5px; background-color: #c8e6c9;')
    
    def add_final_state(self):
        """Add a final state."""
        state = self.final_state_combo.currentText()
        if not state:
            QMessageBox.warning(self, 'Warning', 'Please select a state.')
            return
        
        if state in self.final_states:
            QMessageBox.warning(self, 'Warning', f'State "{state}" is already a final state.')
            return
        
        self.final_states.append(state)
        self.final_states_list.addItem(state)
    
    def remove_final_state(self):
        """Remove selected final state."""
        current_item = self.final_states_list.currentItem()
        if not current_item:
            return
        
        state = current_item.text()
        self.final_states.remove(state)
        self.final_states_list.takeItem(self.final_states_list.currentRow())
    
    def update_combos(self):
        """Update all combo boxes with current states and symbols."""
        # Update state combos
        self.from_state_combo.clear()
        self.to_state_combo.clear()
        self.start_state_combo.clear()
        self.final_state_combo.clear()
        
        self.from_state_combo.addItems(self.states)
        self.to_state_combo.addItems(self.states)
        self.start_state_combo.addItems(self.states)
        self.final_state_combo.addItems(self.states)
        
        # Update symbol combo
        self.symbol_combo.clear()
        self.symbol_combo.addItems(self.alphabet)
    
    def update_transitions_table(self):
        """Update the transitions table."""
        self.transitions_table.setRowCount(0)
        
        for (from_state, symbol), to_state in sorted(self.transitions.items()):
            row = self.transitions_table.rowCount()
            self.transitions_table.insertRow(row)
            self.transitions_table.setItem(row, 0, QTableWidgetItem(from_state))
            self.transitions_table.setItem(row, 1, QTableWidgetItem(symbol))
            self.transitions_table.setItem(row, 2, QTableWidgetItem(to_state))
    
    def export_dfa(self):
        """
        Export the current DFA configuration to a JSON file.
        
        This method allows users to save their DFA to a file while keeping the builder
        dialog open for continued editing. Unlike create_dfa(), this method:
        - Does NOT close the dialog
        - Does NOT set self.dfa (doesn't load into main application)
        - Allows multiple exports with different filenames
        - Validates DFA structure before export
        
        Validation Process:
        1. Required fields: states, alphabet, start_state (must be present)
        2. Optional fields: final_states, complete transitions (warns if missing)
        3. User can choose to export anyway despite warnings
        
        Workflow:
        1. Validate required fields (show error if missing)
        2. Warn about optional fields (user can proceed)
        3. Create temporary DFA object for validation
        4. Open file save dialog
        5. Export to JSON using standard export function
        6. Show success message
        7. Dialog remains open for continued editing
        
        Use Cases:
        - Save work in progress
        - Create backups before major changes
        - Export multiple versions (v1, v2, etc.)
        - Share DFA with others
        
        Returns:
            None. Shows message boxes for user feedback.
            
        Raises:
            No exceptions raised - all errors are caught and shown to user.
        """
        
        # ============================================================
        # STEP 1: Validate Required Fields
        # ============================================================
        # A valid DFA must have at least one state, one alphabet symbol,
        # and a designated start state. These are non-negotiable requirements.
        
        # Check for states - DFA cannot exist without states
        if not self.states:
            QMessageBox.warning(
                self, 
                'Incomplete', 
                'Please add at least one state before exporting.'
            )
            return  # Exit early if validation fails
        
        # Check for alphabet - DFA needs symbols to process
        if not self.alphabet:
            QMessageBox.warning(
                self, 
                'Incomplete', 
                'Please add at least one symbol before exporting.'
            )
            return  # Exit early if validation fails
        
        # Check for start state - DFA must know where to begin
        if not self.start_state:
            QMessageBox.warning(
                self, 
                'Incomplete', 
                'Please set a start state before exporting.'
            )
            return  # Exit early if validation fails
        
        # ============================================================
        # STEP 2: Warn About Missing Final States (Optional)
        # ============================================================
        # Final states are technically optional, but a DFA without them
        # will reject ALL strings. We warn the user but allow export.
        
        if not self.final_states:
            # Ask user if they want to proceed without final states
            reply = QMessageBox.question(
                self, 
                'No Final States',
                'No final states defined. This DFA will reject all strings. Export anyway?',
                QMessageBox.Yes | QMessageBox.No
            )
            # If user chooses No, cancel the export
            if reply == QMessageBox.No:
                return
        
        # ============================================================
        # STEP 3: Check for Incomplete Transitions (Optional)
        # ============================================================
        # A complete DFA should have a transition for every (state, symbol) pair.
        # Missing transitions may cause runtime errors, so we warn the user.
        
        missing = []  # List to store missing transitions
        
        # Check every possible (state, symbol) combination
        for state in self.states:
            for symbol in self.alphabet:
                # If this combination doesn't have a transition, record it
                if (state, symbol) not in self.transitions:
                    missing.append(f"({state}, {symbol})")
        
        # If there are missing transitions, warn the user
        if missing:
            # Show first 5 missing transitions (to avoid overwhelming message)
            missing_preview = ", ".join(missing[:5])
            # Add "..." if there are more than 5 missing
            if len(missing) > 5:
                missing_preview += "..."
            
            # Ask user if they want to proceed with incomplete transitions
            reply = QMessageBox.question(
                self, 
                'Incomplete Transitions',
                f'Missing transitions: {missing_preview}\n\n'
                f'Total missing: {len(missing)}\n\n'
                f'Export anyway? (DFA may not work correctly)',
                QMessageBox.Yes | QMessageBox.No
            )
            # If user chooses No, cancel the export
            if reply == QMessageBox.No:
                return
        
        # ============================================================
        # STEP 4: Create Temporary DFA and Export
        # ============================================================
        # If we reach here, user has confirmed they want to export.
        # We create a temporary DFA object to validate the structure
        # and then export it to JSON.
        
        try:
            # Create a temporary DFA object for validation and export
            # This does NOT set self.dfa (which would load it into the app)
            # Note: Lists are converted to sets as required by DFA class
            temp_dfa = DFA(
                states=set(self.states),           # Convert list to set
                alphabet=set(self.alphabet),       # Convert list to set
                transitions=self.transitions,      # Already a dict
                start_state=self.start_state,      # String
                final_states=set(self.final_states)  # Convert list to set
            )
            
            # ============================================================
            # STEP 5: Open File Save Dialog
            # ============================================================
            # Let user choose where to save the file
            # Default filename: 'my_dfa.json'
            # File filter: Only show .json files by default
            
            filename, _ = QFileDialog.getSaveFileName(
                self,                              # Parent widget
                'Export DFA as JSON',              # Dialog title
                'my_dfa.json',                     # Default filename
                'JSON Files (*.json);;All Files (*)'  # File type filters
            )
            
            # ============================================================
            # STEP 6: Export to JSON File
            # ============================================================
            # If user didn't cancel the dialog (filename is not empty)
            
            if filename:
                # Import the export function (lazy import to avoid circular dependencies)
                from dfa import export_dfa_to_json
                
                # Export the DFA to the chosen file
                # This uses the standard export function from dfa.py
                export_dfa_to_json(temp_dfa, filename)
                
                # Show success message to user
                # Note: Dialog stays open for continued editing
                QMessageBox.information(
                    self, 
                    'Success', 
                    f'DFA exported to {filename}\n\n'
                    f'You can continue editing or click "Create DFA" to load it.'
                )
                
        except Exception as e:
            # ============================================================
            # STEP 7: Handle Any Errors
            # ============================================================
            # Catch any errors that occur during DFA creation or export
            # This includes:
            # - DFA validation errors (invalid structure)
            # - File I/O errors (permissions, disk full, etc.)
            # - Any other unexpected errors
            
            QMessageBox.critical(
                self, 
                'Error', 
                f'Failed to export DFA:\n{str(e)}'
            )
            # Note: We don't re-raise the exception - just show it to user
            # This keeps the dialog open so user can fix issues
    
    def create_dfa(self):
        """Create the DFA and close dialog."""
        # Validate
        if not self.states:
            QMessageBox.warning(self, 'Incomplete', 'Please add at least one state.')
            return
        
        if not self.alphabet:
            QMessageBox.warning(self, 'Incomplete', 'Please add at least one symbol.')
            return
        
        if not self.start_state:
            QMessageBox.warning(self, 'Incomplete', 'Please set a start state.')
            return
        
        if not self.final_states:
            reply = QMessageBox.question(
                self, 'No Final States',
                'No final states defined. This DFA will reject all strings. Continue?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Check if transition function is complete
        missing = []
        for state in self.states:
            for symbol in self.alphabet:
                if (state, symbol) not in self.transitions:
                    missing.append(f"({state}, {symbol})")
        
        if missing:
            reply = QMessageBox.question(
                self, 'Incomplete Transitions',
                f'Missing transitions: {", ".join(missing[:5])}{"..." if len(missing) > 5 else ""}\n\n'
                f'Total missing: {len(missing)}\n\n'
                f'A complete DFA requires transitions for all (state, symbol) pairs.\n'
                f'Continue anyway? (May cause errors)',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Try to create DFA
        try:
            self.dfa = DFA(
                states=set(self.states),
                alphabet=set(self.alphabet),
                transitions=self.transitions,
                start_state=self.start_state,
                final_states=set(self.final_states)
            )
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to create DFA:\n{str(e)}')
    
    def get_dfa(self):
        """Return the created DFA."""
        return self.dfa if hasattr(self, 'dfa') else None
    
    def load_existing_dfa(self, dfa):
        """Load an existing DFA into the builder for editing."""
        # Load states
        self.states = sorted(list(dfa.states))
        for state in self.states:
            self.states_list.addItem(state)
        
        # Load alphabet
        self.alphabet = sorted(list(dfa.alphabet))
        for symbol in self.alphabet:
            self.alphabet_list.addItem(symbol)
        
        # Load transitions
        self.transitions = dict(dfa.transitions)
        self.update_transitions_table()
        
        # Load start state
        self.start_state = dfa.start_state
        self.start_state_label.setText(f'Start State: {self.start_state}')
        self.start_state_label.setStyleSheet('padding: 5px; background-color: #c8e6c9;')
        
        # Load final states
        self.final_states = sorted(list(dfa.final_states))
        for state in self.final_states:
            self.final_states_list.addItem(state)
        
        # Update all combo boxes
        self.update_combos()
