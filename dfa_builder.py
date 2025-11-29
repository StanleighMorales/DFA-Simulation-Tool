"""
DFA Builder - GUI for manually creating DFAs
"""
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
    QPushButton, QListWidget, QGroupBox, QMessageBox, QTableWidget,
    QTableWidgetItem, QHeaderView, QComboBox, QFileDialog
)
from PyQt5.QtCore import Qt
from dfa import DFA


class DFABuilderDialog(QDialog):
    """Dialog for manually creating a DFA."""
    
    def __init__(self, parent=None, existing_dfa=None):
        super().__init__(parent)
        self.setWindowTitle('Edit DFA' if existing_dfa else 'Create DFA Manually')
        self.setGeometry(150, 150, 800, 600)
        self.setModal(True)
        
        self.states = []
        self.alphabet = []
        self.transitions = {}
        self.start_state = None
        self.final_states = []
        
        self.init_ui()
        
        # Load existing DFA if provided
        if existing_dfa:
            self.load_existing_dfa(existing_dfa)
    
    def init_ui(self):
        """Initialize the user interface."""
        main_layout = QVBoxLayout()
        self.setLayout(main_layout)
        
        # Title
        title = QLabel('Build Your DFA')
        title.setStyleSheet('font-size: 18px; font-weight: bold; padding: 10px;')
        title.setAlignment(Qt.AlignCenter)
        main_layout.addWidget(title)
        
        # Instructions
        instructions = QLabel(
            'Create a DFA by defining states, alphabet, transitions, start state, and final states.'
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet('padding: 5px; background-color: #e3f2fd; border-radius: 3px;')
        main_layout.addWidget(instructions)
        
        # Content layout (two columns)
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
        
        # Bottom buttons
        button_layout = QHBoxLayout()
        
        export_btn = QPushButton('💾 Export as JSON')
        export_btn.setStyleSheet('background-color: #9C27B0; color: white; padding: 10px;')
        export_btn.clicked.connect(self.export_dfa)
        button_layout.addWidget(export_btn)
        
        create_btn = QPushButton('✓ Create DFA')
        create_btn.setStyleSheet('background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;')
        create_btn.clicked.connect(self.create_dfa)
        button_layout.addWidget(create_btn)
        
        cancel_btn = QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
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
        """Export the current DFA configuration to a JSON file."""
        # Validate basic requirements
        if not self.states:
            QMessageBox.warning(self, 'Incomplete', 'Please add at least one state before exporting.')
            return
        
        if not self.alphabet:
            QMessageBox.warning(self, 'Incomplete', 'Please add at least one symbol before exporting.')
            return
        
        if not self.start_state:
            QMessageBox.warning(self, 'Incomplete', 'Please set a start state before exporting.')
            return
        
        # Warn about missing final states
        if not self.final_states:
            reply = QMessageBox.question(
                self, 'No Final States',
                'No final states defined. This DFA will reject all strings. Export anyway?',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Check for incomplete transitions
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
                f'Export anyway? (DFA may not work correctly)',
                QMessageBox.Yes | QMessageBox.No
            )
            if reply == QMessageBox.No:
                return
        
        # Try to create and export DFA
        try:
            temp_dfa = DFA(
                states=set(self.states),
                alphabet=set(self.alphabet),
                transitions=self.transitions,
                start_state=self.start_state,
                final_states=set(self.final_states)
            )
            
            # Open file dialog
            filename, _ = QFileDialog.getSaveFileName(
                self, 'Export DFA as JSON', 'my_dfa.json', 'JSON Files (*.json);;All Files (*)'
            )
            
            if filename:
                from dfa import export_dfa_to_json
                export_dfa_to_json(temp_dfa, filename)
                QMessageBox.information(
                    self, 'Success', 
                    f'DFA exported to {filename}\n\nYou can continue editing or click "Create DFA" to load it.'
                )
        except Exception as e:
            QMessageBox.critical(self, 'Error', f'Failed to export DFA:\n{str(e)}')
    
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
