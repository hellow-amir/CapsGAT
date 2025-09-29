import sys
import re
import json
import csv
import os
from pathlib import Path
from PyQt5.QtWidgets import (QApplication, QMainWindow, QVBoxLayout, QHBoxLayout, 
                             QTextEdit, QListWidget, QPushButton, QWidget, QLabel, 
                             QFileDialog, QMessageBox, QSpinBox, QShortcut, QFrame,
                             QInputDialog, QLineEdit, QDialog, QDialogButtonBox, 
                             QGridLayout, QPlainTextEdit, QCheckBox, QTabWidget, QRadioButton)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QFont, QKeySequence, QColor, QTextCharFormat, QSyntaxHighlighter, QIcon

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

class TextSelectionDialog(QDialog):
    def __init__(self, block_text, parent=None):
        super().__init__(parent)
        self.block_text = block_text
        self.start_pos = 0
        self.end_pos = 0
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Select Text")
        self.setGeometry(300, 300, 700, 300)
        
        layout = QVBoxLayout(self)
        
        instructions = QLabel("Use ← → arrows to adjust selection, Shift+arrows to extend, then press Enter:")
        instructions.setStyleSheet("font-weight: bold;")
        layout.addWidget(instructions)
        
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setMaximumHeight(100)
        self.text_display.setStyleSheet("font-family: monospace; font-size: 14px;")
        layout.addWidget(self.text_display)
        
        self.selection_label = QLabel("Selection: (none)")
        layout.addWidget(self.selection_label)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        for button in button_box.buttons():
            button.setFocusPolicy(Qt.NoFocus)
            
        layout.addWidget(button_box)
        
        self.update_display()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left and not event.modifiers() & Qt.ShiftModifier:
            if self.start_pos > 0:
                self.start_pos -= 1
                self.end_pos = self.start_pos
            self.update_display()
            event.accept()
        elif event.key() == Qt.Key_Right and not event.modifiers() & Qt.ShiftModifier:
            if self.end_pos < len(self.block_text):
                self.start_pos += 1
                self.end_pos = self.start_pos
            self.update_display()
            event.accept()
        elif event.key() == Qt.Key_Left and event.modifiers() & Qt.ShiftModifier:
            if self.start_pos > 0:
                self.start_pos -= 1
            self.update_display()
            event.accept()
        elif event.key() == Qt.Key_Right and event.modifiers() & Qt.ShiftModifier:
            if self.end_pos < len(self.block_text):
                self.end_pos += 1
            self.update_display()
            event.accept()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.accept()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def update_display(self):
        before_text = self.block_text[:self.start_pos]
        selected_text = self.block_text[self.start_pos:self.end_pos]
        after_text = self.block_text[self.end_pos:]
        
        html_content = f"""
        <div style="font-family: monospace; font-size: 14px; padding: 10px;">
            <span style="background-color: #e0e0e0; padding: 5px; border-radius: 3px;">{before_text}</span>
            <span style="background-color: #ffcc00; padding: 5px; border-radius: 3px;">{selected_text}</span>
            <span style="background-color: #e0e0e0; padding: 5px; border-radius: 3px;">{after_text}</span>
        </div>
        """
        
        self.text_display.setHtml(html_content)
        
        if self.start_pos == self.end_pos:
            self.selection_label.setText(f"Selection: (none) - Position: {self.start_pos}")
        else:
            self.selection_label.setText(f"Selection: '{selected_text}' (positions {self.start_pos}-{self.end_pos})")
    
    def get_selection(self):
        return self.start_pos, self.end_pos, self.block_text[self.start_pos:self.end_pos]

class BlockSplitDialog(QDialog):
    def __init__(self, block_text, parent=None):
        super().__init__(parent)
        self.block_text = block_text
        self.split_position = 0
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Split Block")
        self.setGeometry(300, 300, 700, 250)
        
        layout = QVBoxLayout(self)
        
        instructions = QLabel("Use ← → arrows to position split, then press Enter to confirm:")
        instructions.setStyleSheet("font-weight: bold;")
        layout.addWidget(instructions)
        
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setMaximumHeight(100)
        self.text_display.setStyleSheet("font-family: monospace; font-size: 14px;")
        layout.addWidget(self.text_display)
        
        self.cursor_label = QLabel("Split position: 0")
        layout.addWidget(self.cursor_label)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        for button in button_box.buttons():
            button.setFocusPolicy(Qt.NoFocus)
            
        layout.addWidget(button_box)
        
        self.update_display()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.split_position = max(0, self.split_position - 1)
            self.update_display()
            event.accept()
        elif event.key() == Qt.Key_Right:
            self.split_position = min(len(self.block_text), self.split_position + 1)
            self.update_display()
            event.accept()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter, Qt.Key_Space):
            self.accept()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def update_display(self):
        before_text = self.block_text[:self.split_position]
        after_text = self.block_text[self.split_position:]
        
        html_content = f"""
        <div style="font-family: monospace; font-size: 14px; padding: 10px;">
            <span style="background-color: #c8f7c8; padding: 5px; border-radius: 3px;">{before_text}</span>
            <span style="background-color: #f7c8c8; padding: 5px; border-radius: 3px;">{after_text}</span>
        </div>
        """
        
        self.text_display.setHtml(html_content)
        self.cursor_label.setText(f"Split position: {self.split_position} (text will be split after character {self.split_position})")

class EnhancedPauseDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_option = 0
        self.pause_options = [
            "(.)", "(-)", "(--)", "(---)", "(_._)", "(())", "<<>>", "[ ]",
            "°h", "°hh", "°hhh", "h°", "hh°", "hhh°"
        ]
        self.pause_descriptions = [
            "micropause", "short pause", "medium pause", "long pause", 
            "measured pause", "comment", "action", "overlap",
            "short inhale", "medium inhale", "long inhale", 
            "short exhale", "medium exhale", "long exhale"
        ]
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Insert GAT2 Symbol")
        self.setGeometry(300, 300, 650, 350)
        
        layout = QVBoxLayout(self)
        
        # Create a grid to show all options with highlighting
        self.option_widget = QWidget()
        option_layout = QGridLayout(self.option_widget)
        
        self.option_labels = []
        for i, (symbol, desc) in enumerate(zip(self.pause_options, self.pause_descriptions)):
            label = QLabel(f"<b>{symbol}</b>")
            label.setAlignment(Qt.AlignCenter)
            label.setToolTip(desc)
            label.setStyleSheet("""
                QLabel {
                    border: 2px solid #ccc;
                    border-radius: 8px;
                    padding: 15px;
                    margin: 3px;
                    background-color: #f0f0f0;
                    font-size: 14px;
                }
                QLabel:hover {
                    background-color: #e0e0e0;
                }
            """)
            label.setMinimumSize(80, 60)
            label.mousePressEvent = lambda event, idx=i: self.label_clicked(idx)
            option_layout.addWidget(label, i // 4, i % 4)
            self.option_labels.append(label)
        
        layout.addWidget(self.option_widget)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        for button in button_box.buttons():
            button.setFocusPolicy(Qt.NoFocus)
            
        layout.addWidget(button_box)
        
        self.update_display()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        
    def label_clicked(self, index):
        self.selected_option = index
        self.update_display()
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.selected_option = (self.selected_option - 1) % len(self.pause_options)
            self.update_display()
            event.accept()
        elif event.key() == Qt.Key_Right:
            self.selected_option = (self.selected_option + 1) % len(self.pause_options)
            self.update_display()
            event.accept()
        elif event.key() == Qt.Key_Up:
            self.selected_option = (self.selected_option - 4) % len(self.pause_options)
            self.update_display()
            event.accept()
        elif event.key() == Qt.Key_Down:
            self.selected_option = (self.selected_option + 4) % len(self.pause_options)
            self.update_display()
            event.accept()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.accept()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def update_display(self):
        # Update all labels, highlighting the selected one
        for i, label in enumerate(self.option_labels):
            if i == self.selected_option:
                label.setStyleSheet("""
                    QLabel {
                        border: 3px solid #ff6600;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 3px;
                        background-color: #fff0cc;
                        font-weight: bold;
                        font-size: 14px;
                    }
                """)
            else:
                label.setStyleSheet("""
                    QLabel {
                        border: 2px solid #ccc;
                        border-radius: 8px;
                        padding: 15px;
                        margin: 3px;
                        background-color: #f0f0f0;
                        font-size: 14px;
                    }
                    QLabel:hover {
                        background-color: #e0e0e0;
                    }
                """)

class PlacementDialog(QDialog):
    def __init__(self, current_text, symbol, parent=None):
        super().__init__(parent)
        self.current_text = current_text
        self.symbol = symbol
        self.placement_position = 0
        self.create_new_line = False
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Place Symbol")
        self.setGeometry(300, 300, 600, 300)
        
        layout = QVBoxLayout(self)
        
        instructions = QLabel("Use ← → arrows to position, Enter to confirm, N for new line:")
        instructions.setStyleSheet("font-weight: bold;")
        layout.addWidget(instructions)
        
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setMaximumHeight(100)
        self.text_display.setStyleSheet("font-family: monospace; font-size: 14px;")
        layout.addWidget(self.text_display)
        
        self.option_label = QLabel("Placement: Insert in current line (Press N to create new line)")
        layout.addWidget(self.option_label)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        for button in button_box.buttons():
            button.setFocusPolicy(Qt.NoFocus)
            
        layout.addWidget(button_box)
        
        self.update_display()
        self.setFocusPolicy(Qt.StrongFocus)
        self.setFocus()
        
    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Left:
            self.placement_position = max(0, self.placement_position - 1)
            self.update_display()
            event.accept()
        elif event.key() == Qt.Key_Right:
            self.placement_position = min(len(self.current_text), self.placement_position + 1)
            self.update_display()
            event.accept()
        elif event.key() == Qt.Key_N:
            self.create_new_line = not self.create_new_line
            self.update_display()
            event.accept()
        elif event.key() in (Qt.Key_Return, Qt.Key_Enter):
            self.accept()
            event.accept()
        else:
            super().keyPressEvent(event)
    
    def update_display(self):
        if self.create_new_line:
            html_content = f"""
            <div style="font-family: monospace; font-size: 14px; padding: 10px;">
                <span style="background-color: #e0e0e0; padding: 5px; border-radius: 3px;">{self.current_text}</span><br>
                <span style="background-color: #c8f7c8; padding: 5px; border-radius: 3px;">{self.symbol}</span>
            </div>
            """
            self.option_label.setText("Placement: Create new line with symbol (Press N for inline)")
        else:
            before_text = self.current_text[:self.placement_position]
            after_text = self.current_text[self.placement_position:]
            html_content = f"""
            <div style="font-family: monospace; font-size: 14px; padding: 10px;">
                <span style="background-color: #e0e0e0; padding: 5px; border-radius: 3px;">{before_text}</span>
                <span style="background-color: #c8f7c8; padding: 5px; border-radius: 3px;">{self.symbol}</span>
                <span style="background-color: #e0e0e0; padding: 5px; border-radius: 3px;">{after_text}</span>
            </div>
            """
            self.option_label.setText("Placement: Insert in current line (Press N to create new line)")
        
        self.text_display.setHtml(html_content)

class CommentDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.comment_text = ""
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Add Comment")
        self.setGeometry(300, 300, 500, 200)
        
        layout = QVBoxLayout(self)
        
        instructions = QLabel("Enter your comment (will be formatted as ((comment))):")
        instructions.setStyleSheet("font-weight: bold;")
        layout.addWidget(instructions)
        
        self.comment_edit = QLineEdit()
        self.comment_edit.setPlaceholderText("Enter comment here")
        layout.addWidget(self.comment_edit)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.comment_edit.setFocus()
        
    def get_comment(self):
        return f"(({self.comment_edit.text()}))"

class EditDialog(QDialog):
    def __init__(self, current_text, parent=None):
        super().__init__(parent)
        self.edited_text = current_text
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Edit Segment Content")
        self.setGeometry(300, 300, 600, 300)
        
        layout = QVBoxLayout(self)
        
        instructions = QLabel("Edit the segment content:")
        instructions.setStyleSheet("font-weight: bold;")
        layout.addWidget(instructions)
        
        self.text_edit = QPlainTextEdit()
        self.text_edit.setPlainText(self.edited_text)
        self.text_edit.setStyleSheet("font-family: monospace; font-size: 14px;")
        layout.addWidget(self.text_edit)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
        self.text_edit.setFocus()
        
    def get_text(self):
        return self.text_edit.toPlainText()

class JsonImportDialog(QDialog):
    def __init__(self, has_tokens=False, parent=None):
        super().__init__(parent)
        self.import_option = "one_block"  # one_block, tokens, auto_segment
        self.has_tokens = has_tokens
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("JSON Import Options")
        self.setGeometry(300, 300, 500, 250)
        
        layout = QVBoxLayout(self)
        
        instructions = QLabel("How would you like to import this JSON file?")
        instructions.setStyleSheet("font-weight: bold;")
        layout.addWidget(instructions)
        
        self.one_block_radio = QRadioButton("Import as one continuous block")
        self.one_block_radio.setChecked(True)
        layout.addWidget(self.one_block_radio)
        
        if self.has_tokens:
            self.tokens_radio = QRadioButton("Import each token as separate block")
            layout.addWidget(self.tokens_radio)
            
            self.auto_radio = QRadioButton("Auto-segment based on pause detection")
            layout.addWidget(self.auto_radio)
        
        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        layout.addWidget(button_box)
        
    def get_import_option(self):
        if self.has_tokens:
            if self.one_block_radio.isChecked():
                return "one_block"
            elif self.tokens_radio.isChecked():
                return "tokens"
            else:
                return "auto_segment"
        else:
            return "one_block"

class ExportPreviewDialog(QDialog):
    def __init__(self, parent=None, has_timestamps=True):
        super().__init__(parent)
        self.include_timestamps = has_timestamps
        self.current_include_timestamps = has_timestamps
        self.export_format = "html"  # Default to HTML
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("Export Preview")
        self.setGeometry(100, 100, 800, 600)
        
        layout = QVBoxLayout(self)
        
        # Format selection - use radio buttons
        format_layout = QHBoxLayout()
        format_layout.addWidget(QLabel("Export Format:"))
        
        self.html_radio = QRadioButton("HTML (.html)")
        self.html_radio.setChecked(True)
        self.html_radio.toggled.connect(self.on_format_changed)
        
        self.txt_radio = QRadioButton("Plain Text (.txt)")
        self.txt_radio.toggled.connect(self.on_format_changed)
        
        format_layout.addWidget(self.html_radio)
        format_layout.addWidget(self.txt_radio)
        format_layout.addStretch()
        
        # Timestamp option
        timestamp_layout = QHBoxLayout()
        self.timestamp_check = QCheckBox("Include timestamps")
        self.timestamp_check.setChecked(self.include_timestamps)
        self.timestamp_check.setEnabled(self.include_timestamps)
        self.timestamp_check.toggled.connect(self.on_timestamp_changed)
        
        if not self.include_timestamps:
            self.timestamp_check.setToolTip("Timestamps not available for text file imports")
        
        timestamp_layout.addWidget(self.timestamp_check)
        timestamp_layout.addStretch()
        
        # Preview area
        preview_label = QLabel("Preview:")
        preview_label.setFont(QFont("Arial", 12, QFont.Bold))
        
        self.preview_text = QTextEdit()
        self.preview_text.setReadOnly(True)
        self.update_preview()
        
        # Buttons
        button_box = QDialogButtonBox(QDialogButtonBox.Save | QDialogButtonBox.Cancel)
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)
        
        layout.addLayout(format_layout)
        layout.addLayout(timestamp_layout)
        layout.addWidget(preview_label)
        layout.addWidget(self.preview_text)
        layout.addWidget(button_box)
        
    def on_format_changed(self):
        if self.html_radio.isChecked():
            self.export_format = "html"
        else:
            self.export_format = "txt"
        self.update_preview()
        
    def on_timestamp_changed(self, checked):
        self.current_include_timestamps = checked
        from PyQt5.QtCore import QTimer
        QTimer.singleShot(100, self.update_preview)
        
    def update_preview(self):
        # Get the parent to regenerate transcript text with current timestamp setting
        parent = self.parent()
        if hasattr(parent, 'generate_transcript_text'):
            preview_text = parent.generate_transcript_text(include_timestamps=self.current_include_timestamps)
        else:
            preview_text = "Preview not available"
            
        if self.export_format == "html":
            html_content = f"""
            <html>
            <head>
            <style>
            body {{
                font-family: 'Courier New', monospace;
                font-size: 10pt;
                line-height: 1.2;
                margin: 20px;
                white-space: pre;
            }}
            </style>
            </head>
            <body>
            {preview_text}
            </body>
            </html>
            """
            self.preview_text.setHtml(html_content)
        else:
            self.preview_text.setPlainText(preview_text)
    
    def get_export_settings(self):
        return {
            'format': self.export_format,
            'include_timestamps': self.current_include_timestamps
        }

class SRTEditor(QMainWindow):
    def __init__(self):
        super().__init__()
        self.srt_blocks = []
        self.current_block_index = 0
        self.speakers = ["A", "B", "C", "D"]
        self.speaker_colors = [
            QColor(220, 240, 255),  # Light blue
            QColor(255, 220, 220),  # Light red
            QColor(220, 255, 220),  # Light green
            QColor(255, 255, 200)   # Light yellow
        ]
        self.context_blocks = 5
        self.current_file_path = None
        self.file_has_timestamps = True
        self.init_ui()
        
    def init_ui(self):
        self.setWindowTitle("CapsGAT")
        self.setGeometry(100, 100, 1400, 900)
        self.setWindowIcon(QIcon(resource_path('images/logo.ico')))
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        layout = QHBoxLayout(central_widget)
        
        # Left panel - Context display
        left_panel = QVBoxLayout()
        
        # File controls
        file_layout = QHBoxLayout()
        
        self.btn_load = QPushButton("Import File")
        self.btn_load.clicked.connect(self.load_file)
        
        self.btn_load_project = QPushButton("Load Project")
        self.btn_load_project.clicked.connect(self.load_project)
        
        self.btn_save = QPushButton("Save Project")
        self.btn_save.clicked.connect(self.save_project)
        self.btn_save.setEnabled(False)
        
        self.btn_export = QPushButton("Export")
        self.btn_export.clicked.connect(self.export_transcript)
        self.btn_export.setEnabled(False)
        
        file_layout.addWidget(self.btn_load)
        file_layout.addWidget(self.btn_load_project)
        file_layout.addWidget(self.btn_save)
        file_layout.addWidget(self.btn_export)
        file_layout.addStretch()
        
        left_panel.addLayout(file_layout)
        
        # Current block info display
        self.current_info_label = QLabel("No block selected")
        self.current_info_label.setStyleSheet("""
            QLabel {
                background-color: #f0f0f0;
                padding: 10px;
                border: 2px solid #ccc;
                border-radius: 5px;
                font-weight: bold;
            }
        """)
        left_panel.addWidget(self.current_info_label)
        
        # Main content display label
        context_label = QLabel("Transcript Content:")
        context_label.setFont(QFont("Arial", 10, QFont.Bold))
        left_panel.addWidget(context_label)
        
        # Main text display
        self.text_display = QTextEdit()
        self.text_display.setReadOnly(True)
        self.text_display.setFont(QFont("Arial", 12))
        self.text_display.setStyleSheet("""
            QTextEdit {
                background-color: #fafafa;
                border: 2px solid #ddd;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        left_panel.addWidget(self.text_display)
        
        # Navigation buttons
        nav_layout = QHBoxLayout()
        
        self.btn_prev = QPushButton("← Previous (P)")
        self.btn_prev.clicked.connect(self.previous_block)
        
        self.lbl_current = QLabel("Current: -/-")
        
        self.btn_next = QPushButton("Next (N) →")
        self.btn_next.clicked.connect(self.next_block)
        
        self.btn_split = QPushButton("Split (Space)")
        self.btn_split.clicked.connect(self.split_current_block)
        
        self.btn_merge = QPushButton("Merge (Del)")
        self.btn_merge.clicked.connect(self.merge_with_next)
        
        self.btn_edit = QPushButton("Edit (E)")
        self.btn_edit.clicked.connect(self.edit_current_block)
        
        self.btn_unassign = QPushButton("Unassign (U)")
        self.btn_unassign.clicked.connect(self.unassign_current)
        
        self.btn_symbols = QPushButton("Symbols (*)")
        self.btn_symbols.clicked.connect(self.open_pause_dialog)
        
        nav_layout.addWidget(self.btn_prev)
        nav_layout.addWidget(self.lbl_current)
        nav_layout.addWidget(self.btn_next)
        nav_layout.addWidget(self.btn_split)
        nav_layout.addWidget(self.btn_merge)
        nav_layout.addWidget(self.btn_edit)
        nav_layout.addWidget(self.btn_unassign)
        nav_layout.addWidget(self.btn_symbols)
        
        left_panel.addLayout(nav_layout)
        
        # Right panel - Controls
        right_panel = QVBoxLayout()
        
        speaker_label = QLabel("Assign Speaker (Keyboard Shortcuts):")
                      
        speaker_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_panel.addWidget(speaker_label)
     
        self.speaker_container = QWidget()
        self.speaker_layout = QVBoxLayout(self.speaker_container)
        self.create_speaker_widgets()
        right_panel.addWidget(self.speaker_container)
        
        manage_layout = QHBoxLayout()
        self.speaker_edit = QSpinBox()
        self.speaker_edit.setMinimum(2)
        self.speaker_edit.setMaximum(8)
        self.speaker_edit.setValue(4)
        self.speaker_edit.valueChanged.connect(self.update_speaker_count)

        # Add stretch on left, then content, then stretch on right for centering
        manage_layout.addStretch()
        manage_layout.addWidget(QLabel("Number of speakers:"))
        manage_layout.addWidget(self.speaker_edit)
        manage_layout.addStretch()

        right_panel.addLayout(manage_layout)
        
        symbols_label = QLabel("\nGAT2 Symbols:")
        symbols_label.setFont(QFont("Arial", 12, QFont.Bold))
        right_panel.addWidget(symbols_label)
        
        self.btn_open_symbols = QPushButton("Open Symbols Dialog (* key)")
        self.btn_open_symbols.clicked.connect(self.open_pause_dialog)
        self.btn_open_symbols.setStyleSheet("""
            QPushButton {
                background-color: #e0e0ff;
                padding: 10px;
                font-weight: bold;
                border: 2px solid #aaa;
                border-radius: 5px;
            }
        """)
        right_panel.addWidget(self.btn_open_symbols)
        
        right_panel.addWidget(QLabel("Unassigned Blocks:"))
        self.unassigned_list = QListWidget()
        self.unassigned_list.itemDoubleClicked.connect(self.jump_to_block)
        right_panel.addWidget(self.unassigned_list)
                
        instructions = QLabel(
            "Keyboard Shortcuts:\n\n"
            "• 1-4: Assign speakers A-D\n"
            "• N/P or ← →: Navigate blocks\n"
            "• Space: Split block\n"
            "• Del: Merge with next\n"
            "• E: Edit content\n"
            "• U: Unassign speaker\n"
            "• *: GAT2 symbols\n"
            "• .: Insert micropause\n"
            "• Enter: Insert empty line"
        )
        instructions.setWordWrap(True)
        instructions.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        right_panel.addWidget(instructions)
        
        right_panel.addStretch()
        
        layout.addLayout(left_panel, 4)
        layout.addLayout(right_panel, 1)
        
        self.setup_shortcuts()
        
    def create_speaker_widgets(self):
        for i in reversed(range(self.speaker_layout.count())): 
            self.speaker_layout.itemAt(i).widget().setParent(None)
        
        self.speaker_widgets = []
        for i, speaker in enumerate(self.speakers):
            speaker_widget = QWidget()
            speaker_layout = QHBoxLayout(speaker_widget)
            
            color_label = QLabel("■")
            color_label.setStyleSheet(f"color: {self.speaker_colors[i].name()}; font-size: 20px;")
            
            speaker_name_edit = QLineEdit(speaker)
            speaker_name_edit.textChanged.connect(lambda text, idx=i: self.rename_speaker(idx, text))
            speaker_name_edit.setFixedWidth(100)
            
            speaker_btn = QPushButton(f"{i+1}. Assign")
            speaker_btn.clicked.connect(lambda checked, idx=i: self.assign_speaker(idx))
            speaker_btn.setStyleSheet(f"""
                QPushButton {{ 
                    background-color: {self.speaker_colors[i].name()}; 
                    border: 2px solid darkgray;
                    padding: 5px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.speaker_colors[i].lighter(120).name()};
                }}
            """)
            
            speaker_layout.addWidget(color_label)
            speaker_layout.addWidget(QLabel("Name:"))
            speaker_layout.addWidget(speaker_name_edit)
            speaker_layout.addWidget(speaker_btn)
            speaker_layout.addStretch()
            
            self.speaker_layout.addWidget(speaker_widget)
            self.speaker_widgets.append({
                'name_edit': speaker_name_edit,
                'button': speaker_btn
            })
        
    def setup_shortcuts(self):
        for i in range(len(self.speakers)):
            QShortcut(QKeySequence(str(i+1)), self).activated.connect(
                lambda idx=i: self.assign_speaker(idx))
        QShortcut(QKeySequence("N"), self).activated.connect(self.next_block)
        QShortcut(QKeySequence("P"), self).activated.connect(self.previous_block)
        QShortcut(QKeySequence("Right"), self).activated.connect(self.next_block)
        QShortcut(QKeySequence("Left"), self).activated.connect(self.previous_block)
        QShortcut(QKeySequence("Space"), self).activated.connect(self.split_current_block)
        QShortcut(QKeySequence("Delete"), self).activated.connect(self.merge_with_next)
        QShortcut(QKeySequence("E"), self).activated.connect(self.edit_current_block)
        QShortcut(QKeySequence("*"), self).activated.connect(self.open_pause_dialog)
        QShortcut(QKeySequence("p"), self).activated.connect(self.open_pause_dialog)
        QShortcut(QKeySequence("U"), self).activated.connect(self.unassign_current)
        QShortcut(QKeySequence("Return"), self).activated.connect(self.insert_empty_line)
        # FIXED: Changed shortcuts to use placement dialog
        QShortcut(QKeySequence("."), self).activated.connect(lambda: self.handle_pause("(.)"))
        QShortcut(QKeySequence("h"), self).activated.connect(lambda: self.handle_pause("°h"))
        QShortcut(QKeySequence("H"), self).activated.connect(lambda: self.handle_pause("h°"))
        
    def rename_speaker(self, speaker_idx, new_name):
        if speaker_idx < len(self.speakers):
            self.speakers[speaker_idx] = new_name
            self.update_display()
        
    def update_speaker_count(self, count):
        while len(self.speakers) > count:
            self.speakers.pop()
            self.speaker_colors.pop()
        while len(self.speakers) < count:
            new_idx = len(self.speakers)
            self.speakers.append(chr(65 + new_idx))
            self.speaker_colors.append(QColor(200, 200, 200))
        
        self.create_speaker_widgets()
        self.setup_shortcuts()
        self.update_display()
        
    def load_file(self):
        file_path, _ = QFileDialog.getOpenFileName(
            self, "Open File", "", 
            "All Supported Files (*.srt *.txt *.json *.tsv);;SRT Files (*.srt);;Text Files (*.txt);;JSON Files (*.json);;TSV Files (*.tsv)"
        )
        if file_path:
            try:
                file_extension = Path(file_path).suffix.lower()
                
                if file_extension == '.srt':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.srt_blocks = self.parse_srt(content)
                    self.file_has_timestamps = True
                    
                elif file_extension == '.txt':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.srt_blocks = self.parse_text(content)
                    self.file_has_timestamps = False
                    
                elif file_extension == '.json':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = json.load(f)
                    self.srt_blocks = self.parse_json(content)
                    # Check if any blocks have timestamps
                    self.file_has_timestamps = any(block.get('start_time') for block in self.srt_blocks)
                    
                elif file_extension == '.tsv':
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    self.srt_blocks = self.parse_tsv(content)
                    self.file_has_timestamps = True
                
                self.current_block_index = 0
                self.current_file_path = file_path
                self.btn_export.setEnabled(len(self.srt_blocks) > 0)
                self.btn_save.setEnabled(len(self.srt_blocks) > 0)
                self.update_display()
                
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load file: {str(e)}")
    
    def parse_srt(self, content):
        blocks = []
        srt_blocks = content.strip().split('\n\n')
        
        for block in srt_blocks:
            lines = block.strip().split('\n')
            if len(lines) >= 3:
                try:
                    index = int(lines[0].strip())
                    time_line = lines[1].strip()
                    time_match = re.match(r'(\d{2}):(\d{2}):(\d{2}),(\d{3}) --> (\d{2}):(\d{2}):(\d{2}),(\d{3})', time_line)
                    
                    if time_match:
                        text = '\n'.join(lines[2:]).strip()
                        block_data = {
                            'index': index,
                            'start_time': f"{time_match.group(1)}:{time_match.group(2)}:{time_match.group(3)}",
                            'start_ms': int(time_match.group(4)),
                            'end_time': f"{time_match.group(5)}:{time_match.group(6)}:{time_match.group(7)}",
                            'end_ms': int(time_match.group(8)),
                            'text': text,
                            'speaker': None,
                            'is_turn_start': True
                        }
                        blocks.append(block_data)
                except ValueError:
                    continue
        
        return blocks
    
    def parse_text(self, content):
        blocks = []
        lines = content.strip().split('\n')
        
        for i, line in enumerate(lines):
            if line.strip():
                block_data = {
                    'index': i + 1,
                    'start_time': '',
                    'end_time': '',
                    'text': line.strip(),
                    'speaker': None,
                    'is_turn_start': True
                }
                blocks.append(block_data)
        
        return blocks
    
    def parse_tsv(self, content):
        """Parse TSV file with start, end, and text columns"""
        blocks = []
        lines = content.strip().split('\n')
        
        for i, line in enumerate(lines):
            if i == 0:  # Skip header
                continue
                
            parts = line.split('\t')
            if len(parts) >= 3:
                start_ms = int(parts[0])
                end_ms = int(parts[1])
                text = parts[2]
                
                # Convert milliseconds to SRT time format
                start_time = self.ms_to_srt_time(start_ms)
                end_time = self.ms_to_srt_time(end_ms)
                
                block_data = {
                    'index': i,
                    'start_time': start_time,
                    'end_time': end_time,
                    'text': text,
                    'speaker': None,
                    'is_turn_start': True
                }
                blocks.append(block_data)
        
        return blocks
    
    def ms_to_srt_time(self, ms):
        """Convert milliseconds to SRT time format (HH:MM:SS,mmm)"""
        hours = ms // 3600000
        ms %= 3600000
        minutes = ms // 60000
        ms %= 60000
        seconds = ms // 1000
        milliseconds = ms % 1000
        
        return f"{hours:02d}:{minutes:02d}:{seconds:02d},{milliseconds:03d}"
    
    def auto_segment_tokens(self, tokens, timestamps):
        """Auto-segment tokens based on pause detection"""
        if len(tokens) != len(timestamps) or len(tokens) < 2:
            return [{'text': ''.join(tokens), 'start_time': '', 'end_time': ''}]
        
        # Calculate gaps between tokens
        gaps = []
        for i in range(1, len(timestamps)):
            gap = timestamps[i] - timestamps[i-1]
            gaps.append(gap)
        
        # Calculate average gap and threshold for segmentation
        avg_gap = sum(gaps) / len(gaps)
        threshold = avg_gap * 2.5  # Segment when gap is 2.5x average
        
        segments = []
        current_segment = []
        current_start = timestamps[0]
        
        for i, (token, timestamp) in enumerate(zip(tokens, timestamps)):
            current_segment.append(token)
            
            # Check if we should segment after this token
            if i < len(timestamps) - 1:
                gap = timestamps[i+1] - timestamp
                if gap > threshold:
                    # Create segment
                    segment_text = ''.join(current_segment)
                    segments.append({
                        'text': segment_text,
                        'start_time': self.seconds_to_srt_time(current_start),
                        'end_time': self.seconds_to_srt_time(timestamp + gap/2)
                    })
                    current_segment = []
                    if i < len(timestamps) - 1:
                        current_start = timestamps[i+1]
        
        # Add final segment
        if current_segment:
            segment_text = ''.join(current_segment)
            segments.append({
                'text': segment_text,
                'start_time': self.seconds_to_srt_time(current_start),
                'end_time': self.seconds_to_srt_time(timestamps[-1] + avg_gap)
            })
        
        return segments
    
    def seconds_to_srt_time(self, seconds):
        """Convert seconds to SRT time format"""
        hours = int(seconds // 3600)
        minutes = int((seconds % 3600) // 60)
        secs = seconds % 60
        milliseconds = int((secs - int(secs)) * 1000)
        
        return f"{hours:02d}:{minutes:02d}:{int(secs):02d},{milliseconds:03d}"
    
    def parse_json(self, content):
        blocks = []
        
        try:
            # Handle the specific format from your transcription software
            if isinstance(content, dict) and 'tokens' in content and 'timestamps' in content:
                tokens = content['tokens']
                timestamps = content['timestamps']
                
                # Show import options dialog
                dialog = JsonImportDialog(has_tokens=True, parent=self)
                if dialog.exec_() == QDialog.Accepted:
                    option = dialog.get_import_option()
                    
                    if option == "one_block":
                        # Join tokens to form the text
                        text = ''.join(tokens) if tokens else ""
                        block_data = {
                            'index': 1,
                            'start_time': '',
                            'end_time': '',
                            'text': text,
                            'speaker': None,
                            'is_turn_start': True
                        }
                        blocks.append(block_data)
                        
                    elif option == "tokens":
                        # Create a block for each token
                        for i, (token, timestamp) in enumerate(zip(tokens, timestamps)):
                            block_data = {
                                'index': i + 1,
                                'start_time': self.seconds_to_srt_time(timestamp),
                                'end_time': '',
                                'text': token,
                                'speaker': None,
                                'is_turn_start': True
                            }
                            blocks.append(block_data)
                            
                    elif option == "auto_segment":
                        # Auto-segment based on pauses
                        segments = self.auto_segment_tokens(tokens, timestamps)
                        for i, segment in enumerate(segments):
                            block_data = {
                                'index': i + 1,
                                'start_time': segment['start_time'],
                                'end_time': segment['end_time'],
                                'text': segment['text'],
                                'speaker': None,
                                'is_turn_start': True
                            }
                            blocks.append(block_data)
                else:
                    # User canceled
                    return []
                
            # Handle Whisper-style JSON with segments
            elif isinstance(content, dict) and 'segments' in content:
                segments = content['segments']
                for i, segment in enumerate(segments):
                    block_data = {
                        'index': i + 1,
                        'start_time': self.seconds_to_srt_time(segment.get('start', 0)),
                        'end_time': self.seconds_to_srt_time(segment.get('end', 0)),
                        'text': segment.get('text', '').strip(),
                        'speaker': None,
                        'is_turn_start': True
                    }
                    blocks.append(block_data)
                    
            # Handle simple text JSON
            elif isinstance(content, dict) and 'text' in content:
                block_data = {
                    'index': 1,
                    'start_time': '',
                    'end_time': '',
                    'text': content['text'].strip(),
                    'speaker': None,
                    'is_turn_start': True
                }
                blocks.append(block_data)
                
            # Handle other JSON structures
            elif isinstance(content, list):
                for i, item in enumerate(content):
                    if isinstance(item, dict):
                        block_data = {
                            'index': i + 1,
                            'start_time': item.get('start_time', ''),
                            'end_time': item.get('end_time', ''),
                            'text': item.get('text', ''),
                            'speaker': None,
                            'is_turn_start': True
                        }
                        blocks.append(block_data)
            elif isinstance(content, dict):
                transcript_data = content.get('transcript', content.get('blocks', []))
                if isinstance(transcript_data, list):
                    for i, item in enumerate(transcript_data):
                        if isinstance(item, dict):
                            block_data = {
                                'index': i + 1,
                                'start_time': item.get('start_time', ''),
                                'end_time': item.get('end_time', ''),
                                'text': item.get('text', ''),
                                'speaker': None,
                                'is_turn_start': True
                            }
                            blocks.append(block_data)
            
            if not blocks:
                QMessageBox.warning(self, "JSON Format", 
                                   "The JSON file doesn't contain recognizable transcript data.")
                
        except Exception as e:
            QMessageBox.critical(self, "JSON Error", 
                               f"Could not parse JSON file: {str(e)}")
        
        return blocks
    
    def save_project(self):
        if not self.srt_blocks:
            return
            
        file_path, _ = QFileDialog.getSaveFileName(self, "Save Project", "", "GAT2 Project Files (*.gat2)")
        if file_path:
            try:
                project_data = {
                    'srt_blocks': self.srt_blocks,
                    'current_block_index': self.current_block_index,
                    'speakers': self.speakers,
                    'source_file': self.current_file_path,
                    'file_has_timestamps': self.file_has_timestamps
                }
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    json.dump(project_data, f, indent=2, ensure_ascii=False)
                    
                QMessageBox.information(self, "Success", f"Project saved to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not save project: {str(e)}")
    
    def load_project(self):
        file_path, _ = QFileDialog.getOpenFileName(self, "Load Project", "", "GAT2 Project Files (*.gat2)")
        if file_path:
            try:
                with open(file_path, 'r', encoding='utf-8') as f:
                    project_data = json.load(f)
                
                self.srt_blocks = project_data['srt_blocks']
                self.current_block_index = project_data['current_block_index']
                self.speakers = project_data['speakers']
                self.current_file_path = project_data.get('source_file', '')
                self.file_has_timestamps = project_data.get('file_has_timestamps', True)
                
                self.btn_export.setEnabled(len(self.srt_blocks) > 0)
                self.btn_save.setEnabled(len(self.srt_blocks) > 0)
                self.update_display()
                
                QMessageBox.information(self, "Success", f"Project loaded from {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not load project: {str(e)}")

    def update_display(self):
        if not self.srt_blocks:
            self.text_display.setPlainText("No content loaded")
            self.current_info_label.setText("No block selected")
            self.lbl_current.setText("Current: -/-")
            return
        
        current_block = self.srt_blocks[self.current_block_index]
        speaker_name = self.speakers[current_block['speaker']] if current_block['speaker'] is not None else "UNASSIGNED"
        turn_indicator = " [TURN START]" if current_block.get('is_turn_start', True) else " [CONTINUATION]"
        self.current_info_label.setText(
            f"Block {current_block['index']} | Speaker: {speaker_name}{turn_indicator} | "
            f"Time: {current_block['start_time']} --> {current_block['end_time']}"
        )
        
        start_idx = max(0, self.current_block_index - self.context_blocks)
        end_idx = min(len(self.srt_blocks), self.current_block_index + self.context_blocks + 1)
        
        display_text = ""
        for i in range(start_idx, end_idx):
            block = self.srt_blocks[i]
            
            if i == self.current_block_index:
                display_text += f">> {block['text']}\n\n"
            else:
                display_text += f"   {block['text']}\n\n"
        
        self.text_display.setPlainText(display_text)
        
        self.colorize_display()
        
        self.lbl_current.setText(f"Current: {self.current_block_index + 1}/{len(self.srt_blocks)}")
        
        self.unassigned_list.clear()
        for i, block in enumerate(self.srt_blocks):
            if block['speaker'] is None:
                preview = block['text'][:50] + "..." if len(block['text']) > 50 else block['text']
                self.unassigned_list.addItem(f"{i+1}: {preview}")
    
    def colorize_display(self):
        cursor = self.text_display.textCursor()
        cursor.select(cursor.Document)
        
        format_normal = QTextCharFormat()
        format_normal.setBackground(QColor(250, 250, 250))
        cursor.setCharFormat(format_normal)
        
        start_idx = max(0, self.current_block_index - self.context_blocks)
        
        for i in range(start_idx, min(len(self.srt_blocks), self.current_block_index + self.context_blocks + 1)):
            block = self.srt_blocks[i]
            if block['speaker'] is not None and block['speaker'] < len(self.speaker_colors):
                color = self.speaker_colors[block['speaker']]
                
                block_pos = (i - start_idx) * 2
                
                cursor.movePosition(cursor.Start)
                for _ in range(block_pos):
                    cursor.movePosition(cursor.Down)
                
                cursor.movePosition(cursor.Down, cursor.KeepAnchor)
                
                block_format = QTextCharFormat()
                block_format.setBackground(color)
                cursor.setCharFormat(block_format)
        
        current_pos = (self.current_block_index - start_idx) * 2
        cursor.movePosition(cursor.Start)
        for _ in range(current_pos):
            cursor.movePosition(cursor.Down)
        
        cursor.movePosition(cursor.Down, cursor.KeepAnchor)
        current_format = QTextCharFormat()
        current_format.setBackground(QColor(255, 240, 200))
        current_format.setFontWeight(QFont.Bold)
        cursor.setCharFormat(current_format)
        
        self.scroll_to_current_block()
    
    def scroll_to_current_block(self):
        cursor = self.text_display.textCursor()
        cursor.movePosition(cursor.Start)
        
        start_idx = max(0, self.current_block_index - self.context_blocks)
        blocks_before_current = self.current_block_index - start_idx
        
        for _ in range(blocks_before_current * 2):
            cursor.movePosition(cursor.Down)
        
        self.text_display.setTextCursor(cursor)
        self.text_display.ensureCursorVisible()
        
    def previous_block(self):
        if self.current_block_index > 0:
            self.current_block_index -= 1
            self.update_display()
            
    def next_block(self):
        if self.current_block_index < len(self.srt_blocks) - 1:
            self.current_block_index += 1
            self.update_display()
            
    def assign_speaker(self, speaker_idx):
        if not self.srt_blocks or speaker_idx >= len(self.speakers):
            return
            
        current_block = self.srt_blocks[self.current_block_index]
        current_block['speaker'] = speaker_idx
        
        is_turn_start = True
        if self.current_block_index > 0:
            prev_block = self.srt_blocks[self.current_block_index - 1]
            if prev_block['speaker'] == speaker_idx:
                is_turn_start = False
        
        current_block['is_turn_start'] = is_turn_start
        
        for i in range(self.current_block_index + 1, len(self.srt_blocks)):
            if self.srt_blocks[i]['speaker'] == speaker_idx:
                self.srt_blocks[i]['is_turn_start'] = False
            else:
                break
        
        self.find_next_unassigned()
        
    def unassign_current(self):
        if not self.srt_blocks:
            return
            
        current_block = self.srt_blocks[self.current_block_index]
        current_block['speaker'] = None
        current_block['is_turn_start'] = True
        
        for i in range(self.current_block_index + 1, len(self.srt_blocks)):
            if i > 0 and self.srt_blocks[i]['speaker'] is not None:
                prev_speaker = self.srt_blocks[i-1]['speaker']
                current_speaker = self.srt_blocks[i]['speaker']
                self.srt_blocks[i]['is_turn_start'] = (prev_speaker != current_speaker)
        
        self.update_display()
        
    def find_next_unassigned(self):
        start_index = self.current_block_index
        for i in range(1, len(self.srt_blocks) + 1):
            next_index = (start_index + i) % len(self.srt_blocks)
            if self.srt_blocks[next_index]['speaker'] is None:
                self.current_block_index = next_index
                self.update_display()
                return
        
        if self.current_block_index < len(self.srt_blocks) - 1:
            self.current_block_index += 1
            self.update_display()
            
    def split_current_block(self):
        if not self.srt_blocks:
            return
            
        current_block = self.srt_blocks[self.current_block_index]
        dialog = BlockSplitDialog(current_block['text'], self)
        
        if dialog.exec_() == QDialog.Accepted:
            split_pos = dialog.split_position
            if 0 < split_pos < len(current_block['text']):
                text_before = current_block['text'][:split_pos].strip()
                text_after = current_block['text'][split_pos:].strip()
                
                if text_before and text_after:
                    current_block['text'] = text_before
                    
                    new_block = current_block.copy()
                    new_block['text'] = text_after
                    new_block['index'] = max(block['index'] for block in self.srt_blocks) + 1
                    new_block['speaker'] = None
                    new_block['is_turn_start'] = False
                    
                    if current_block['speaker'] is not None:
                        new_block['speaker'] = current_block['speaker']
                        new_block['is_turn_start'] = False
                    
                    self.srt_blocks.insert(self.current_block_index + 1, new_block)
                    self.update_display()
    
    def merge_with_next(self):
        if self.current_block_index >= len(self.srt_blocks) - 1:
            return
            
        current_block = self.srt_blocks[self.current_block_index]
        next_block = self.srt_blocks[self.current_block_index + 1]
        
        if current_block['speaker'] is None or current_block['speaker'] == next_block['speaker']:
            current_block['text'] += " " + next_block['text']
            current_block['end_time'] = next_block['end_time']
            
            if next_block.get('is_turn_start', False):
                current_block['is_turn_start'] = True
            
            del self.srt_blocks[self.current_block_index + 1]
            self.update_display()
    
    def edit_current_block(self):
        if not self.srt_blocks:
            return
            
        current_block = self.srt_blocks[self.current_block_index]
        dialog = EditDialog(current_block['text'], self)
        
        if dialog.exec_() == QDialog.Accepted:
            new_text = dialog.get_text()
            current_block['text'] = new_text
            self.update_display()
    
    def open_pause_dialog(self):
        if not self.srt_blocks:
            return
            
        dialog = EnhancedPauseDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            option_index = dialog.selected_option
            self.handle_gat2_symbol(option_index)
    
    def handle_gat2_symbol(self, option_index):
        symbols = ["(.)", "(-)", "(--)", "(---)", "(_._)", "(())", "<<>>", "[ ]", "°h", "°hh", "°hhh", "h°", "hh°", "hhh°"]
        
        if option_index == 4:  # Measured pause
            self.handle_measured_pause()
        elif option_index == 5:  # Comment
            self.handle_comment()
        elif option_index == 6:  # Action
            self.handle_action()
        elif option_index == 7:  # Overlap
            self.handle_overlap()
        else:  # Pauses and breath sounds
            symbol = symbols[option_index]
            self.handle_pause(symbol)
    
    def handle_measured_pause(self):
        time_ms, ok = QInputDialog.getInt(
            self, 
            "Measured Pause", 
            "Enter pause length in 100 milliseconds (e.g., 8 for 0.8 seconds):",
            value=5, min=1, max=50, step=1
        )
        
        if ok:
            seconds = time_ms / 10.0
            symbol = f"({seconds:.1f})"
            
            current_block = self.srt_blocks[self.current_block_index]
            dialog = PlacementDialog(current_block['text'], symbol, self)
            
            if dialog.exec_() == QDialog.Accepted:
                if dialog.create_new_line:
                    new_block = {
                        'index': max(block['index'] for block in self.srt_blocks) + 1,
                        'start_time': '',
                        'end_time': '',
                        'text': symbol,
                        'speaker': None,
                        'is_turn_start': False,
                        'is_pause': True
                    }
                    self.srt_blocks.insert(self.current_block_index + 1, new_block)
                else:
                    pos = dialog.placement_position
                    current_block['text'] = (current_block['text'][:pos] + " " + symbol + 
                                           " " + current_block['text'][pos:]).strip()
                
                self.update_display()
    
    def handle_pause(self, symbol):
        if not self.srt_blocks:
            return
            
        current_block = self.srt_blocks[self.current_block_index]
        dialog = PlacementDialog(current_block['text'], symbol, self)
        
        if dialog.exec_() == QDialog.Accepted:
            if dialog.create_new_line:
                new_block = {
                    'index': max(block['index'] for block in self.srt_blocks) + 1,
                    'start_time': '',
                    'end_time': '',
                    'text': symbol,
                    'speaker': None,
                    'is_turn_start': False,
                    'is_pause': True
                }
                self.srt_blocks.insert(self.current_block_index + 1, new_block)
            else:
                pos = dialog.placement_position
                current_block['text'] = (current_block['text'][:pos] + " " + symbol + 
                                       " " + current_block['text'][pos:]).strip()
            
            self.update_display()
    
    def handle_comment(self):
        dialog = CommentDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            comment = dialog.get_comment()
            if comment:
                current_block = self.srt_blocks[self.current_block_index]
                placement_dialog = PlacementDialog(current_block['text'], comment, self)
                
                if placement_dialog.exec_() == QDialog.Accepted:
                    if placement_dialog.create_new_line:
                        new_block = {
                            'index': max(block['index'] for block in self.srt_blocks) + 1,
                            'start_time': '',
                            'end_time': '',
                            'text': comment,
                            'speaker': None,
                            'is_turn_start': False,
                            'is_comment': True
                        }
                        self.srt_blocks.insert(self.current_block_index + 1, new_block)
                    else:
                        pos = placement_dialog.placement_position
                        current_block['text'] = (current_block['text'][:pos] + " " + comment + 
                                               " " + current_block['text'][pos:]).strip()
                    
                    self.update_display()
    
    def handle_action(self):
        if not self.srt_blocks:
            return
            
        current_block = self.srt_blocks[self.current_block_index]
        dialog = TextSelectionDialog(current_block['text'], self)
        
        if dialog.exec_() == QDialog.Accepted:
            start_pos, end_pos, selected_text = dialog.get_selection()
            if selected_text:
                action_text, ok = QInputDialog.getText(self, "Action Description", 
                                                     f"Describe the action for '{selected_text}':")
                if ok and action_text:
                    before_text = current_block['text'][:start_pos]
                    after_text = current_block['text'][end_pos:]
                    current_block['text'] = f"{before_text}<<{action_text}> {selected_text}>{after_text}"
                    self.update_display()
    
    def handle_overlap(self):
        if not self.srt_blocks or self.current_block_index == 0:
            QMessageBox.information(self, "Overlap Feature", 
                                   "Overlap requires at least two consecutive blocks.")
            return
            
        current_block = self.srt_blocks[self.current_block_index]
        prev_block = self.srt_blocks[self.current_block_index - 1]
        
        dialog = TextSelectionDialog(current_block['text'], self)
        if dialog.exec_() == QDialog.Accepted:
            start_pos, end_pos, selected_text = dialog.get_selection()
            if selected_text:
                prev_dialog = TextSelectionDialog(prev_block['text'], self)
                prev_dialog.setWindowTitle("Select Overlapping Text in Previous Block")
                if prev_dialog.exec_() == QDialog.Accepted:
                    prev_start, prev_end, prev_selected = prev_dialog.get_selection()
                    if prev_selected:
                        # Calculate indentation for the second line
                        chars_before_overlap = prev_start
                        indent_spaces = " " * chars_before_overlap
                        
                        before_text = current_block['text'][:start_pos]
                        after_text = current_block['text'][end_pos:]
                        current_block['text'] = f"{before_text}{indent_spaces}[{selected_text}]{after_text}"
                        
                        prev_before = prev_block['text'][:prev_start]
                        prev_after = prev_block['text'][prev_end:]
                        prev_block['text'] = f"{prev_before}[{prev_selected}]{prev_after}"
                        
                        self.update_display()
    
    def insert_empty_line(self):
        if not self.srt_blocks:
            return
            
        new_block = {
            'index': max(block['index'] for block in self.srt_blocks) + 1,
            'start_time': '',
            'end_time': '',
            'text': '',
            'speaker': None,
            'is_turn_start': False,
            'is_empty': True
        }
        self.srt_blocks.insert(self.current_block_index + 1, new_block)
        self.current_block_index += 1
        self.update_display()
    
    def jump_to_block(self, item):
        text = item.text()
        match = re.match(r'(\d+):', text)
        if match:
            block_idx = int(match.group(1)) - 1
            if 0 <= block_idx < len(self.srt_blocks):
                self.current_block_index = block_idx
                self.update_display()
    
    def export_transcript(self):
        if not self.srt_blocks:
            return
            
        preview_dialog = ExportPreviewDialog(self, self.file_has_timestamps)
        if preview_dialog.exec_() == QDialog.Accepted:
            settings = preview_dialog.get_export_settings()
            transcript_text = self.generate_transcript_text(include_timestamps=settings['include_timestamps'])
            self.final_export(transcript_text, settings)
    
    def generate_transcript_text(self, include_timestamps=True):
        total_lines = len([b for b in self.srt_blocks if b.get('speaker') is not None or b.get('is_pause') or b.get('is_comment') or b.get('is_empty')])
        line_digits = len(str(total_lines))
        
        max_speaker_length = 0
        for block in self.srt_blocks:
            if block['speaker'] is not None and block.get('is_turn_start', True):
                speaker_label = self.speakers[block['speaker']] + ":"
                max_speaker_length = max(max_speaker_length, len(speaker_label))
        
        max_speaker_length = max(max_speaker_length, 2)
        
        output_lines = []
        line_number = 1
        
        for block in self.srt_blocks:
            if block.get('is_pause') or block.get('is_comment') or block.get('is_empty'):
                if block['text']:
                    padded_line_num = str(line_number).zfill(line_digits)
                    
                    if include_timestamps:
                        timestamp_spaces = " " * 13
                        # Fixed: Use consistent indentation for all non-speaker lines
                        speaker_spaces = " " * (max_speaker_length + 3)
                        line = f"{timestamp_spaces}{padded_line_num}   {speaker_spaces}{block['text']}"
                    else:
                        # FIXED: Use consistent indentation matching speaker lines
                        speaker_spaces = " " * (max_speaker_length + 3)
                        line = f"{padded_line_num}   {speaker_spaces}{block['text']}"
                    
                    output_lines.append(line)
                    line_number += 1
            elif block['speaker'] is not None:
                padded_line_num = str(line_number).zfill(line_digits)
                
                if include_timestamps and block.get('start_time'):
                    time_parts = block['start_time'].split(':')
                    seconds_part = time_parts[2].split(',')[0] if ',' in time_parts[2] else time_parts[2]
                    gat_time = f"{{{time_parts[0]}:{time_parts[1]}:{seconds_part}}}"
                else:
                    gat_time = ""
                
                speaker_label = self.speakers[block['speaker']]
                
                if block.get('is_turn_start', True):
                    formatted_speaker = f"{speaker_label}:".ljust(max_speaker_length)
                    # Fixed: Exactly 3 spaces after speaker name
                    if include_timestamps and gat_time:
                        line = f"{gat_time}   {padded_line_num}   {formatted_speaker}   {block['text']}"
                    else:
                        line = f"{padded_line_num}   {formatted_speaker}   {block['text']}"
                else:
                    if include_timestamps:
                        timestamp_spaces = " " * 13
                        # Fixed: Consistent indentation for continuation lines
                        speaker_spaces = " " * (max_speaker_length + 3)
                        line = f"{timestamp_spaces}{padded_line_num}   {speaker_spaces}{block['text']}"
                    else:
                        # FIXED: Consistent indentation for continuation lines
                        speaker_spaces = " " * (max_speaker_length + 3)
                        line = f"{padded_line_num}   {speaker_spaces}{block['text']}"
                
                output_lines.append(line)
                line_number += 1
        
        # Remove leading spaces from the very first line
        if output_lines:
            # For HTML export, we need to ensure no leading spaces in the body
            output_lines[0] = output_lines[0].lstrip()
        
        return '\n'.join(output_lines)
    
    def final_export(self, transcript_text, settings):
        file_ext = ".html" if settings['format'] == 'html' else ".txt"
        file_path, _ = QFileDialog.getSaveFileName(
            self, f"Export Transcript", "", 
            f"{settings['format'].upper()} Files (*{file_ext})"
        )
        
        if file_path:
            try:
                if settings['format'] == 'html':
                    # FIXED: Ensure no leading spaces in HTML body
                    clean_transcript = transcript_text.lstrip()
                    html_content = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="UTF-8">
<title>GAT2 Transcript</title>
<style>
body {{
    font-family: 'Courier New', monospace;
    font-size: 10pt;
    line-height: 1.2;
    margin: 20px;
    white-space: pre;
}}
</style>
</head>
<body>
{clean_transcript}
</body>
</html>"""
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(html_content)
                else:
                    with open(file_path, 'w', encoding='utf-8') as f:
                        f.write(transcript_text)
                
                QMessageBox.information(self, "Success", f"Transcript exported to {file_path}")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Could not export file: {str(e)}")

def main():
    app = QApplication(sys.argv)
    editor = SRTEditor()
    editor.show()
    sys.exit(app.exec_())

if __name__ == '__main__':
    main()