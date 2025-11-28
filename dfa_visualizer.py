"""
DFA Visualizer - GUI application using PyQt5 and NetworkX
"""
import sys
import networkx as nx
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QFileDialog, QMessageBox, QTextEdit,
    QScrollArea, QDialog
)
from PyQt5.QtCore import Qt

from dfa import DFA, import_dfa_from_json, is_accepted, trace_execution
from dfa_builder import DFABuilderDialog


class DFACanvas(FigureCanvas):
    """Canvas for drawing DFA graphs using NetworkX and Matplotlib."""
    
    def __init__(self, parent=None, width=8, height=6, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super().__init__(self.fig)
        self.setParent(parent)
        
        self.dfa = None
        self.highlighted_path = []
    
    def set_dfa(self, dfa):
        """Set the DFA to visualize."""
        self.dfa = dfa
        self.highlighted_path = []
        self.draw_dfa()
    
    def highlight_path(self, states):
        """Highlight a path through the DFA."""
        self.highlighted_path = states
        self.draw_dfa()
    
    def draw_dfa(self):
        """Draw the DFA graph with proper visual distinctions."""
        self.axes.clear()
        
        if self.dfa is None:
            self.axes.text(0.5, 0.5, 'No DFA loaded', 
                          ha='center', va='center', fontsize=14)
            self.draw()
            return
        
        # Create directed graph
        G = nx.DiGraph()
        
        # Add nodes (states)
        for state in self.dfa.states:
            G.add_node(state)
        
        # Add edges (transitions) with labels
        edge_labels = {}
        for (state, symbol), next_state in self.dfa.transitions.items():
            # Group multiple symbols for same transition
            edge_key = (state, next_state)
            if edge_key in edge_labels:
                edge_labels[edge_key] += f", {symbol}"
            else:
                edge_labels[edge_key] = symbol
                G.add_edge(state, next_state)
        
        # Layout - use spring layout for better visualization
        pos = nx.spring_layout(G, k=2, iterations=50, seed=42)
        
        # Draw different node types
        regular_nodes = [n for n in G.nodes() 
                        if n != self.dfa.start_state and n not in self.dfa.final_states]
        start_only = [self.dfa.start_state] if self.dfa.start_state not in self.dfa.final_states else []
        final_only = [n for n in self.dfa.final_states if n != self.dfa.start_state]
        start_and_final = [n for n in self.dfa.final_states if n == self.dfa.start_state]
        
        # Highlighted nodes
        highlighted = [n for n in self.highlighted_path if n in G.nodes()]
        non_highlighted_regular = [n for n in regular_nodes if n not in highlighted]
        
        # Draw regular states (single circle)
        if non_highlighted_regular:
            nx.draw_networkx_nodes(G, pos, nodelist=non_highlighted_regular,
                                  node_color='lightblue', node_size=800,
                                  ax=self.axes)
        
        # Draw highlighted regular states
        if highlighted and regular_nodes:
            highlighted_regular = [n for n in highlighted if n in regular_nodes]
            if highlighted_regular:
                nx.draw_networkx_nodes(G, pos, nodelist=highlighted_regular,
                                      node_color='yellow', node_size=800,
                                      ax=self.axes)
        
        # Draw start state (arrow will be added separately)
        if start_only:
            nx.draw_networkx_nodes(G, pos, nodelist=start_only,
                                  node_color='lightgreen', node_size=800,
                                  ax=self.axes)
        
        # Draw final states (double circle)
        if final_only:
            # Outer circle
            nx.draw_networkx_nodes(G, pos, nodelist=final_only,
                                  node_color='lightcoral', node_size=1000,
                                  ax=self.axes)
            # Inner circle
            nx.draw_networkx_nodes(G, pos, nodelist=final_only,
                                  node_color='lightcoral', node_size=800,
                                  ax=self.axes)
        
        # Draw start+final states (double circle with green)
        if start_and_final:
            # Outer circle
            nx.draw_networkx_nodes(G, pos, nodelist=start_and_final,
                                  node_color='lightgreen', node_size=1000,
                                  ax=self.axes)
            # Inner circle
            nx.draw_networkx_nodes(G, pos, nodelist=start_and_final,
                                  node_color='lightgreen', node_size=800,
                                  ax=self.axes)
        
        # Draw edges
        nx.draw_networkx_edges(G, pos, edge_color='gray', 
                              arrows=True, arrowsize=20, 
                              arrowstyle='-|>', connectionstyle='arc3,rad=0.15',
                              width=2, ax=self.axes,
                              min_source_margin=15, min_target_margin=15)
        
        # Draw edge labels (transition symbols)
        formatted_edge_labels = {k: v for k, v in edge_labels.items()}
        nx.draw_networkx_edge_labels(G, pos, formatted_edge_labels,
                                     font_size=10, ax=self.axes)
        
        # Draw node labels (state names)
        nx.draw_networkx_labels(G, pos, font_size=12, font_weight='bold',
                               ax=self.axes)
        
        # Draw arrow pointing to start state
        if self.dfa.start_state in pos:
            start_pos = pos[self.dfa.start_state]
            arrow_start = (start_pos[0] - 0.15, start_pos[1] + 0.15)
            arrow_end = (start_pos[0] - 0.05, start_pos[1] + 0.05)
            self.axes.annotate('', xy=arrow_end, xytext=arrow_start,
                             arrowprops=dict(arrowstyle='->', lw=2, color='green'))
            self.axes.text(arrow_start[0] - 0.05, arrow_start[1] + 0.05, 'start',
                          fontsize=10, color='green', weight='bold')
        
        # Title with DFA info - legend removed to prevent overlap
        self.axes.set_title(f'DFA Visualization - {len(self.dfa.states)} states, '
                           f'{len(self.dfa.alphabet)} symbols', fontsize=12, weight='bold')
        self.axes.axis('off')
        self.draw()


class DFAVisualizerWindow(QMainWindow):
    """Main application window for DFA visualization."""
    
    def __init__(self):
        super().__init__()
        self.dfa = None
        self.init_ui()
    
    def init_ui(self):
        """Initialize the user interface."""
        self.setWindowTitle('DFA Visualizer')
        self.setGeometry(100, 100, 1200, 800)
        
        # Central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Left panel - Controls (with scroll area)
        left_scroll = QScrollArea()
        left_scroll.setWidgetResizable(True)
        left_scroll.setMinimumWidth(300)
        left_scroll.setMaximumWidth(400)
        
        left_widget = QWidget()
        left_panel = QVBoxLayout()
        left_widget.setLayout(left_panel)
        
        # Title
        title = QLabel('DFA Visualizer')
        title.setStyleSheet('font-size: 18px; font-weight: bold; padding: 10px;')
        title.setAlignment(Qt.AlignCenter)
        left_panel.addWidget(title)
        
        # Load, Create, and Clear DFA buttons
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
        
        left_panel.addLayout(btn_layout)
        
        # DFA info
        self.info_label = QLabel('No DFA loaded')
        self.info_label.setWordWrap(True)
        self.info_label.setStyleSheet('padding: 10px; background-color: #f0f0f0; border-radius: 5px;')
        left_panel.addWidget(self.info_label)
        
        # Test string section
        test_label = QLabel('Test String:')
        test_label.setStyleSheet('font-weight: bold; margin-top: 10px;')
        left_panel.addWidget(test_label)
        
        self.test_input = QLineEdit()
        self.test_input.setPlaceholderText('Enter string to test...')
        self.test_input.returnPressed.connect(self.test_string)
        left_panel.addWidget(self.test_input)
        
        test_btn = QPushButton('Test String')
        test_btn.clicked.connect(self.test_string)
        left_panel.addWidget(test_btn)
        
        # Result display
        self.result_label = QLabel('')
        self.result_label.setWordWrap(True)
        self.result_label.setStyleSheet('padding: 10px; margin-top: 5px;')
        left_panel.addWidget(self.result_label)
        
        # Trace button
        trace_btn = QPushButton('Show Step-by-Step Trace')
        trace_btn.clicked.connect(self.show_trace)
        left_panel.addWidget(trace_btn)
        
        # Trace output
        trace_label = QLabel('Execution Trace:')
        trace_label.setStyleSheet('font-weight: bold; margin-top: 10px;')
        left_panel.addWidget(trace_label)
        
        self.trace_output = QTextEdit()
        self.trace_output.setReadOnly(True)
        self.trace_output.setMaximumHeight(200)
        left_panel.addWidget(self.trace_output)
        
        # Clear button
        clear_btn = QPushButton('Clear Visualization')
        clear_btn.clicked.connect(self.clear_visualization)
        left_panel.addWidget(clear_btn)
        
        # Visual legend
        legend_label = QLabel(
            '<b>Visual Guide:</b><br>'
            '🔵 <span style="color: #87CEEB;">Regular State</span><br>'
            '🔴 <span style="color: #F08080;">Final State (double circle)</span><br>'
            '🟢 <span style="color: #90EE90;">Start State (with arrow)</span><br>'
            '🟡 <span style="color: #FFD700;">Highlighted Path</span>'
        )
        legend_label.setWordWrap(True)
        legend_label.setStyleSheet('padding: 8px; background-color: #fffef0; border-radius: 5px; font-size: 10px; margin-top: 10px;')
        left_panel.addWidget(legend_label)
        
        # Finish left panel scroll area setup
        left_scroll.setWidget(left_widget)
        
        # Right panel - Graph visualization
        right_panel = QVBoxLayout()
        
        self.canvas = DFACanvas(self, width=8, height=6, dpi=100)
        right_panel.addWidget(self.canvas)
        
        # Add panels to main layout with fixed left panel width
        main_layout.addWidget(left_scroll)
        main_layout.addLayout(right_panel, 1)
    
    def load_dfa(self):
        """Load a DFA from JSON file."""
        filename, _ = QFileDialog.getOpenFileName(
            self, 'Load DFA', '', 'JSON Files (*.json);;All Files (*)'
        )
        
        if filename:
            try:
                self.dfa = import_dfa_from_json(filename)
                self.canvas.set_dfa(self.dfa)
                
                # Update info label
                info_text = (
                    f"<b>DFA Loaded Successfully</b><br>"
                    f"States: {', '.join(sorted(self.dfa.states))}<br>"
                    f"Alphabet: {', '.join(sorted(self.dfa.alphabet))}<br>"
                    f"Start State: {self.dfa.start_state}<br>"
                    f"Final States: {', '.join(sorted(self.dfa.final_states))}<br>"
                    f"Transitions: {len(self.dfa.transitions)}"
                )
                self.info_label.setText(info_text)
                
                self.result_label.setText('')
                self.trace_output.clear()
                
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
                    f"States: {', '.join(sorted(self.dfa.states))}<br>"
                    f"Alphabet: {', '.join(sorted(self.dfa.alphabet))}<br>"
                    f"Start State: {self.dfa.start_state}<br>"
                    f"Final States: {', '.join(sorted(self.dfa.final_states))}<br>"
                    f"Transitions: {len(self.dfa.transitions)}"
                )
                self.info_label.setText(info_text)
                
                self.result_label.setText('')
                self.trace_output.clear()
    
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
            self.info_label.setText('No DFA loaded')
            self.result_label.setText('')
            self.trace_output.clear()
            self.test_input.clear()
    
    def test_string(self):
        """Test a string against the loaded DFA."""
        if self.dfa is None:
            QMessageBox.warning(self, 'Warning', 'Please load a DFA first.')
            return
        
        test_str = self.test_input.text()
        
        try:
            accepted = is_accepted(self.dfa, test_str)
            
            if accepted:
                self.result_label.setText(
                    f"<span style='color: green; font-weight: bold; font-size: 14px;'>"
                    f"✓ ACCEPTED</span><br>"
                    f"String '{test_str}' is accepted by the DFA."
                )
                self.result_label.setStyleSheet('padding: 10px; background-color: #d4edda; border-radius: 5px;')
            else:
                self.result_label.setText(
                    f"<span style='color: red; font-weight: bold; font-size: 14px;'>"
                    f"✗ REJECTED</span><br>"
                    f"String '{test_str}' is rejected by the DFA."
                )
                self.result_label.setStyleSheet('padding: 10px; background-color: #f8d7da; border-radius: 5px;')
            
        except ValueError as e:
            QMessageBox.warning(self, 'Invalid Input', str(e))
    
    def show_trace(self):
        """Show step-by-step execution trace."""
        if self.dfa is None:
            QMessageBox.warning(self, 'Warning', 'Please load a DFA first.')
            return
        
        test_str = self.test_input.text()
        
        try:
            trace_text = f"Tracing execution of: '{test_str}'\n"
            trace_text += "=" * 50 + "\n\n"
            
            states_visited = []
            
            for step in trace_execution(self.dfa, test_str):
                states_visited.append(step['current_state'])
                
                if step['symbol'] is None and not step['is_final_step']:
                    trace_text += f"Initial State: {step['current_state']}\n"
                    trace_text += f"Input: '{step['remaining_input']}'\n\n"
                elif step['is_final_step']:
                    result = "ACCEPTED ✓" if step['accepted'] else "REJECTED ✗"
                    trace_text += f"Final State: {step['current_state']}\n"
                    trace_text += f"Result: {result}\n"
                else:
                    trace_text += f"Step {step['step_number']}: Read '{step['symbol']}'\n"
                    trace_text += f"  {step['current_state']} → {step['next_state']}\n"
                    trace_text += f"  Processed: '{step['processed_input']}'\n"
                    trace_text += f"  Remaining: '{step['remaining_input']}'\n\n"
            
            self.trace_output.setText(trace_text)
            
            # Highlight the path in the visualization
            self.canvas.highlight_path(states_visited)
            
        except ValueError as e:
            QMessageBox.warning(self, 'Invalid Input', str(e))
    
    def clear_visualization(self):
        """Clear the current visualization."""
        self.dfa = None
        self.canvas.set_dfa(None)
        self.info_label.setText('No DFA loaded')
        self.result_label.setText('')
        self.trace_output.clear()
        self.test_input.clear()


def main():
    """Main entry point for the application."""
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Modern look
    
    window = DFAVisualizerWindow()
    window.show()
    
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
