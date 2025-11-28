"""
Interactive Step-by-Step DFA Debugger
Enhanced GUI with step-through execution and visual highlighting
"""
import sys
import networkx as nx
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox, QTextEdit,
    QGroupBox, QScrollArea, QDialog
)
from PyQt5.QtCore import Qt

from dfa import DFA, import_dfa_from_json, trace_execution
from dfa_builder import DFABuilderDialog


class InteractiveDFACanvas(FigureCanvasQTAgg):
    """Canvas for interactive DFA visualization with step highlighting."""
    
    def __init__(self, parent=None, width=10, height=7, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.dfa = None
        self.graph = None
        self.pos = None
        self.edge_labels = {}
        
        # Highlighting state
        self.current_state = None
        self.previous_state = None
        self.current_edge = None
        self.all_visited_states = []
    
    def set_dfa(self, dfa):
        """Set the DFA and prepare graph structure."""
        self.dfa = dfa
        self.reset_highlighting()
        self._prepare_graph()
        self.draw_dfa()
    
    def reset_highlighting(self):
        """Reset all highlighting."""
        self.current_state = None
        self.previous_state = None
        self.current_edge = None
        self.all_visited_states = []
    
    def highlight_step(self, current_state, previous_state=None, edge=None):
        """
        Highlight current step in execution.
        
        Args:
            current_state: State to highlight as current
            previous_state: Previous state (for edge highlighting)
            edge: Tuple (from_state, to_state) for edge highlighting
        """
        self.current_state = current_state
        self.previous_state = previous_state
        self.current_edge = edge
        
        if current_state and current_state not in self.all_visited_states:
            self.all_visited_states.append(current_state)
        
        self.draw_dfa()
    
    def _prepare_graph(self):
        """Prepare NetworkX graph structure."""
        if self.dfa is None:
            return
        
        self.graph = nx.DiGraph()
        
        # Add nodes
        for state in self.dfa.states:
            self.graph.add_node(state)
        
        # Add edges and collect labels
        self.edge_labels = {}
        for (state, symbol), next_state in self.dfa.transitions.items():
            edge_key = (state, next_state)
            if edge_key in self.edge_labels:
                self.edge_labels[edge_key] += f", {symbol}"
            else:
                self.edge_labels[edge_key] = symbol
                self.graph.add_edge(state, next_state)
        
        # Calculate layout once
        self.pos = nx.spring_layout(self.graph, k=2.5, iterations=50, seed=42)
    
    def draw_dfa(self):
        """Draw the DFA with current highlighting."""
        self.axes.clear()
        
        if self.dfa is None or self.graph is None:
            self.axes.text(0.5, 0.5, 'No DFA loaded', 
                          ha='center', va='center', fontsize=14)
            self.draw()
            return
        
        G = self.graph
        pos = self.pos
        
        # Categorize nodes for different visual styles
        regular = []
        start_only = []
        final_only = []
        both = []
        
        for state in G.nodes():
            is_start = (state == self.dfa.start_state)
            is_final = (state in self.dfa.final_states)
            is_current = (state == self.current_state)
            is_visited = (state in self.all_visited_states)
            
            # Skip current state - will draw separately
            if is_current:
                continue
            
            if is_start and is_final:
                both.append(state)
            elif is_start:
                start_only.append(state)
            elif is_final:
                final_only.append(state)
            else:
                regular.append(state)
        
        # Separate visited from unvisited
        visited_regular = [s for s in regular if s in self.all_visited_states]
        unvisited_regular = [s for s in regular if s not in self.all_visited_states]
        
        # Draw unvisited regular states
        if unvisited_regular:
            nx.draw_networkx_nodes(G, pos, nodelist=unvisited_regular,
                                  node_color='lightblue', node_size=1000,
                                  ax=self.axes)
        
        # Draw visited regular states (lighter)
        if visited_regular:
            nx.draw_networkx_nodes(G, pos, nodelist=visited_regular,
                                  node_color='#b3d9ff', node_size=1000,
                                  ax=self.axes, alpha=0.7)
        
        # Draw start state
        if start_only:
            nx.draw_networkx_nodes(G, pos, nodelist=start_only,
                                  node_color='lightgreen', node_size=1000,
                                  ax=self.axes)
        
        # Draw final states (double circle)
        if final_only:
            nx.draw_networkx_nodes(G, pos, nodelist=final_only,
                                  node_color='lightcoral', node_size=1200,
                                  ax=self.axes)
            nx.draw_networkx_nodes(G, pos, nodelist=final_only,
                                  node_color='lightcoral', node_size=1000,
                                  ax=self.axes)
        
        # Draw start+final states
        if both:
            nx.draw_networkx_nodes(G, pos, nodelist=both,
                                  node_color='lightgreen', node_size=1200,
                                  ax=self.axes)
            nx.draw_networkx_nodes(G, pos, nodelist=both,
                                  node_color='lightgreen', node_size=1000,
                                  ax=self.axes)
        
        # Draw CURRENT state with special highlighting
        if self.current_state and self.current_state in pos:
            is_final = self.current_state in self.dfa.final_states
            
            # Pulsing yellow highlight
            if is_final:
                # Double circle for final state
                nx.draw_networkx_nodes(G, pos, nodelist=[self.current_state],
                                      node_color='gold', node_size=1400,
                                      ax=self.axes, linewidths=4,
                                      edgecolors='orange')
                nx.draw_networkx_nodes(G, pos, nodelist=[self.current_state],
                                      node_color='gold', node_size=1200,
                                      ax=self.axes)
            else:
                # Single circle
                nx.draw_networkx_nodes(G, pos, nodelist=[self.current_state],
                                      node_color='gold', node_size=1200,
                                      ax=self.axes, linewidths=4,
                                      edgecolors='orange')
        
        # Draw edges
        regular_edges = [e for e in G.edges() if e != self.current_edge]
        
        # Regular edges (gray)
        if regular_edges:
            nx.draw_networkx_edges(G, pos, edgelist=regular_edges,
                                  edge_color='gray', arrows=True,
                                  arrowsize=20, arrowstyle='-|>',
                                  connectionstyle='arc3,rad=0.15',
                                  width=2, ax=self.axes, alpha=0.6,
                                  min_source_margin=15, min_target_margin=15)
        
        # Highlighted edge (current transition)
        if self.current_edge and self.current_edge in G.edges():
            nx.draw_networkx_edges(G, pos, edgelist=[self.current_edge],
                                  edge_color='red', arrows=True,
                                  arrowsize=30, arrowstyle='-|>',
                                  connectionstyle='arc3,rad=0.15',
                                  width=5, ax=self.axes,
                                  min_source_margin=15, min_target_margin=15)
        
        # Draw edge labels
        nx.draw_networkx_edge_labels(G, pos, self.edge_labels,
                                     font_size=11, ax=self.axes)
        
        # Draw node labels
        nx.draw_networkx_labels(G, pos, font_size=13, font_weight='bold',
                               ax=self.axes)
        
        # Draw start arrow
        if self.dfa.start_state in pos:
            start_pos = pos[self.dfa.start_state]
            arrow_start = (start_pos[0] - 0.15, start_pos[1] + 0.15)
            arrow_end = (start_pos[0] - 0.05, start_pos[1] + 0.05)
            self.axes.annotate('', xy=arrow_end, xytext=arrow_start,
                             arrowprops=dict(arrowstyle='->', lw=3, color='green'))
            self.axes.text(arrow_start[0] - 0.05, arrow_start[1] + 0.05,
                          'start', fontsize=11, color='green', weight='bold')
        
        # Title only - legend removed to prevent overlap
        # (Legend info is already in the left panel)
        self.axes.set_title('Interactive DFA Debugger', fontsize=14, weight='bold')
        self.axes.axis('off')
        self.draw()


class InteractiveDebuggerWindow(QMainWindow):
    """Main window for interactive step-by-step debugging."""
    
    def __init__(self):
        super().__init__()
        self.dfa = None
        self.trace_steps = []
        self.current_step_index = -1
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('Interactive DFA Step-by-Step Debugger')
        self.setGeometry(100, 100, 1400, 900)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left panel - Controls (with scroll area)
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setMinimumWidth(350)
        left_scroll.setMaximumWidth(450)
        
        left_widget = QWidget()
        left_panel = QVBoxLayout()
        left_panel.setSpacing(10)
        left_widget.setLayout(left_panel)
        
        # Title
        title = QLabel('Step-by-Step Debugger')
        title.setStyleSheet('font-size: 20px; font-weight: bold; padding: 10px;')
        title.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(title)
        
        # Load DFA section
        load_group = QGroupBox("1. Load DFA")
        load_layout = QVBoxLayout()
        
        # Load, Create, and Clear buttons
        btn_layout = QHBoxLayout()
        
        load_btn = QPushButton('📁 Load')
        load_btn.clicked.connect(self.load_dfa)
        btn_layout.addWidget(load_btn)
        
        create_btn = QPushButton('✏️ Create')
        create_btn.clicked.connect(self.create_dfa)
        create_btn.setStyleSheet('background-color: #2196F3; color: white;')
        btn_layout.addWidget(create_btn)
        
        clear_dfa_btn = QPushButton('🗑️ Clear')
        clear_dfa_btn.clicked.connect(self.clear_dfa)
        clear_dfa_btn.setStyleSheet('background-color: #f44336; color: white;')
        btn_layout.addWidget(clear_dfa_btn)
        
        load_layout.addLayout(btn_layout)
        
        self.dfa_info = QLabel('No DFA loaded')
        self.dfa_info.setWordWrap(True)
        self.dfa_info.setStyleSheet('padding: 8px; background-color: #f0f0f0; border-radius: 5px;')
        load_layout.addWidget(self.dfa_info)
        
        load_group.setLayout(load_layout)
        left_panel.addWidget(load_group)
        
        # Input string section
        input_group = QGroupBox("2. Enter Test String")
        input_layout = QVBoxLayout()
        
        self.input_field = QLineEdit()
        self.input_field.setPlaceholderText('Enter string to debug...')
        self.input_field.setStyleSheet('padding: 8px; font-size: 14px;')
        input_layout.addWidget(self.input_field)
        
        run_btn = QPushButton('▶ Run / Reset')
        run_btn.setStyleSheet('background-color: #4CAF50; color: white; padding: 10px; font-weight: bold;')
        run_btn.clicked.connect(self.run_debug)
        input_layout.addWidget(run_btn)
        
        input_group.setLayout(input_layout)
        left_panel.addWidget(input_group)
        
        # Step controls section
        step_group = QGroupBox("3. Step Through Execution")
        step_layout = QVBoxLayout()
        
        # Step buttons
        btn_layout = QHBoxLayout()
        
        self.step_btn = QPushButton('⏭ Next Step')
        self.step_btn.setEnabled(False)
        self.step_btn.setStyleSheet('padding: 10px; font-weight: bold;')
        self.step_btn.clicked.connect(self.next_step)
        btn_layout.addWidget(self.step_btn)
        
        self.prev_btn = QPushButton('⏮ Previous')
        self.prev_btn.setEnabled(False)
        self.prev_btn.setStyleSheet('padding: 10px;')
        self.prev_btn.clicked.connect(self.prev_step)
        btn_layout.addWidget(self.prev_btn)
        
        step_layout.addLayout(btn_layout)
        
        # Auto-play button
        self.auto_btn = QPushButton('⏯ Auto Play')
        self.auto_btn.setEnabled(False)
        self.auto_btn.clicked.connect(self.auto_play)
        step_layout.addWidget(self.auto_btn)
        
        step_group.setLayout(step_layout)
        left_panel.addWidget(step_group)
        
        # Current step info
        info_group = QGroupBox("Current Step Information")
        info_layout = QVBoxLayout()
        
        self.step_counter = QLabel('Step: -/-')
        self.step_counter.setStyleSheet('font-size: 16px; font-weight: bold; padding: 5px;')
        info_layout.addWidget(self.step_counter)
        
        self.symbol_label = QLabel('Symbol: -')
        self.symbol_label.setStyleSheet('font-size: 14px; padding: 5px; background-color: #e3f2fd; border-radius: 3px;')
        info_layout.addWidget(self.symbol_label)
        
        self.state_label = QLabel('Current State: -')
        self.state_label.setStyleSheet('font-size: 14px; padding: 5px; background-color: #fff3e0; border-radius: 3px;')
        info_layout.addWidget(self.state_label)
        
        self.transition_label = QLabel('Transition: -')
        self.transition_label.setStyleSheet('font-size: 14px; padding: 5px; background-color: #f3e5f5; border-radius: 3px;')
        info_layout.addWidget(self.transition_label)
        
        self.processed_label = QLabel('Processed: ""')
        self.processed_label.setStyleSheet('font-size: 13px; padding: 5px;')
        info_layout.addWidget(self.processed_label)
        
        self.remaining_label = QLabel('Remaining: ""')
        self.remaining_label.setStyleSheet('font-size: 13px; padding: 5px;')
        info_layout.addWidget(self.remaining_label)
        
        info_group.setLayout(info_layout)
        left_panel.addWidget(info_group)
        
        # Result display
        self.result_label = QLabel('')
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet('padding: 10px; font-size: 14px; font-weight: bold;')
        left_panel.addWidget(self.result_label)
        
        # Execution log
        log_label = QLabel('Execution Log:')
        log_label.setStyleSheet('font-weight: bold; margin-top: 5px;')
        left_panel.addWidget(log_label)
        
        self.log_output = QTextEdit()
        self.log_output.setReadOnly(True)
        self.log_output.setMaximumHeight(150)
        self.log_output.setStyleSheet('font-family: monospace; font-size: 11px;')
        left_panel.addWidget(self.log_output)
        
        # Visual legend
        legend_label = QLabel(
            '<b>Visual Guide:</b><br>'
            '🔵 <span style="color: #87CEEB;">Regular State</span><br>'
            '🔴 <span style="color: #F08080;">Final State (double circle)</span><br>'
            '🟢 <span style="color: #90EE90;">Start State (with arrow)</span><br>'
            '🟡 <span style="color: #FFD700;">Current State (gold border)</span><br>'
            '🔴 <span style="color: red;">Current Transition (red arrow)</span>'
        )
        legend_label.setWordWrap(True)
        legend_label.setStyleSheet('padding: 8px; background-color: #fffef0; border-radius: 5px; font-size: 10px;')
        left_panel.addWidget(legend_label)
        
        # Finish left panel scroll area setup
        left_scroll.setWidget(left_widget)
        
        # Right panel - Visualization
        right_panel = QVBoxLayout()
        
        self.canvas = InteractiveDFACanvas(self, width=10, height=7, dpi=100)
        right_panel.addWidget(self.canvas)
        
        # Add panels to main layout with fixed left panel width
        main_layout.addWidget(left_scroll)
        main_layout.addLayout(right_panel, 1)
    
    def load_dfa(self):
        """Load DFA from JSON file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, 'Load DFA', '', 'JSON Files (*.json);;All Files (*)'
        )
        
        if filename:
            try:
                self.dfa = import_dfa_from_json(filename)
                self.canvas.set_dfa(self.dfa)
                
                info_text = (
                    f"<b>Loaded:</b> {filename.split('/')[-1]}<br>"
                    f"<b>States:</b> {len(self.dfa.states)}<br>"
                    f"<b>Alphabet:</b> {{{', '.join(sorted(self.dfa.alphabet))}}}<br>"
                    f"<b>Start:</b> {self.dfa.start_state}<br>"
                    f"<b>Final:</b> {{{', '.join(sorted(self.dfa.final_states))}}}"
                )
                self.dfa_info.setText(info_text)
                
                self.reset_debug()
                
            except Exception as e:
                QMessageBox.critical(self, 'Error', f'Failed to load DFA:\n{str(e)}')
    
    def create_dfa(self):
        """Open DFA builder dialog to create a DFA manually."""
        builder = DFABuilderDialog(self)
        if builder.exec_() == QDialog.Accepted:
            dfa = builder.get_dfa()
            if dfa:
                self.dfa = dfa
                self.canvas.set_dfa(self.dfa)
                
                info_text = (
                    f"<b>Created Manually</b><br>"
                    f"<b>States:</b> {len(self.dfa.states)}<br>"
                    f"<b>Alphabet:</b> {{{', '.join(sorted(self.dfa.alphabet))}}}<br>"
                    f"<b>Start:</b> {self.dfa.start_state}<br>"
                    f"<b>Final:</b> {{{', '.join(sorted(self.dfa.final_states))}}}"
                )
                self.dfa_info.setText(info_text)
                
                self.reset_debug()
    
    def clear_dfa(self):
        """Clear the loaded DFA and reset everything."""
        reply = QMessageBox.question(
            self, 'Clear DFA',
            'Are you sure you want to clear the loaded DFA?',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.dfa = None
            self.canvas.set_dfa(None)
            self.dfa_info.setText('No DFA loaded')
            self.reset_debug()
            self.input_field.clear()
    
    def run_debug(self):
        """Initialize debugging session."""
        if self.dfa is None:
            QMessageBox.warning(self, 'Warning', 'Please load a DFA first.')
            return
        
        test_str = self.input_field.text()
        
        try:
            # Generate all steps
            self.trace_steps = list(trace_execution(self.dfa, test_str))
            self.current_step_index = -1
            
            # Enable controls
            self.step_btn.setEnabled(True)
            self.prev_btn.setEnabled(False)
            self.auto_btn.setEnabled(True)
            
            # Reset display
            self.canvas.reset_highlighting()
            self.canvas.draw_dfa()
            self.result_label.setText('')
            self.log_output.clear()
            
            # Show initial message
            self.log_output.append(f"=== Debugging: '{test_str}' ===")
            self.log_output.append(f"Total steps: {len(self.trace_steps)}")
            self.log_output.append("Click 'Next Step' to begin...\n")
            
            # Move to first step
            self.next_step()
            
        except ValueError as e:
            QMessageBox.warning(self, 'Invalid Input', str(e))
    
    def next_step(self):
        """Move to next step in execution."""
        if not self.trace_steps or self.current_step_index >= len(self.trace_steps) - 1:
            return
        
        self.current_step_index += 1
        self.display_step()
        
        # Update button states
        self.prev_btn.setEnabled(self.current_step_index > 0)
        self.step_btn.setEnabled(self.current_step_index < len(self.trace_steps) - 1)
    
    def prev_step(self):
        """Move to previous step in execution."""
        if not self.trace_steps or self.current_step_index <= 0:
            return
        
        self.current_step_index -= 1
        self.display_step()
        
        # Update button states
        self.prev_btn.setEnabled(self.current_step_index > 0)
        self.step_btn.setEnabled(self.current_step_index < len(self.trace_steps) - 1)
    
    def display_step(self):
        """Display current step information and update visualization."""
        if not self.trace_steps or self.current_step_index < 0:
            return
        
        step = self.trace_steps[self.current_step_index]
        
        # Update step counter
        self.step_counter.setText(f"Step: {self.current_step_index + 1}/{len(self.trace_steps)}")
        
        # Determine edge to highlight
        edge = None
        if step['symbol'] and step['next_state']:
            edge = (step['current_state'], step['next_state'])
        
        # Update visualization
        self.canvas.highlight_step(
            current_state=step['current_state'],
            previous_state=step.get('next_state'),
            edge=edge
        )
        
        # Update info labels
        if step['symbol'] is None and not step['is_final_step']:
            # Initial step
            self.symbol_label.setText('Symbol: [Initial]')
            self.state_label.setText(f"Current State: {step['current_state']}")
            self.transition_label.setText('Transition: -')
            self.processed_label.setText('Processed: ""')
            self.remaining_label.setText(f"Remaining: \"{step['remaining_input']}\"")
            
            self.log_output.append(f"▶ Initial state: {step['current_state']}")
            
        elif step['is_final_step']:
            # Final step
            self.symbol_label.setText('Symbol: [Final]')
            self.state_label.setText(f"Final State: {step['current_state']}")
            self.transition_label.setText('Transition: -')
            self.processed_label.setText(f"Processed: \"{step['processed_input']}\"")
            self.remaining_label.setText('Remaining: ""')
            
            result = "ACCEPTED ✓" if step['accepted'] else "REJECTED ✗"
            color = '#d4edda' if step['accepted'] else '#f8d7da'
            text_color = 'green' if step['accepted'] else 'red'
            
            self.result_label.setText(
                f"<span style='color: {text_color}; font-size: 16px;'>{result}</span>"
            )
            self.result_label.setStyleSheet(f'padding: 10px; background-color: {color}; border-radius: 5px;')
            
            self.log_output.append(f"\n{'='*40}")
            self.log_output.append(f"■ {result}")
            self.log_output.append(f"Final state: {step['current_state']}")
            self.log_output.append(f"In accept states: {step['current_state'] in self.dfa.final_states}")
            
        else:
            # Transition step
            self.symbol_label.setText(f"Symbol: '{step['symbol']}'")
            self.state_label.setText(f"Current State: {step['current_state']}")
            self.transition_label.setText(f"Transition: {step['current_state']} → {step['next_state']}")
            self.processed_label.setText(f"Processed: \"{step['processed_input']}\"")
            self.remaining_label.setText(f"Remaining: \"{step['remaining_input']}\"")
            
            self.log_output.append(
                f"Step {step['step_number']}: Read '{step['symbol']}' | "
                f"{step['current_state']} → {step['next_state']}"
            )
    
    def auto_play(self):
        """Auto-play through all steps."""
        from PyQt5.QtCore import QTimer
        
        if not self.trace_steps:
            return
        
        # Reset to beginning if at end
        if self.current_step_index >= len(self.trace_steps) - 1:
            self.current_step_index = -1
        
        def play_next():
            if self.current_step_index < len(self.trace_steps) - 1:
                self.next_step()
                QTimer.singleShot(800, play_next)  # 800ms delay between steps
        
        play_next()
    
    def reset_debug(self):
        """Reset debugging state."""
        self.trace_steps = []
        self.current_step_index = -1
        self.step_btn.setEnabled(False)
        self.prev_btn.setEnabled(False)
        self.auto_btn.setEnabled(False)
        self.result_label.setText('')
        self.log_output.clear()
        self.step_counter.setText('Step: -/-')
        self.symbol_label.setText('Symbol: -')
        self.state_label.setText('Current State: -')
        self.transition_label.setText('Transition: -')
        self.processed_label.setText('Processed: ""')
        self.remaining_label.setText('Remaining: ""')


def main():
    """Main entry point."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')
    
    window = InteractiveDebuggerWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
