"""Simple file upload dialog for uploading up to 2 files for processing and saving content to user settings."""

import os
from pathlib import Path
from typing import List, Optional

from PyQt6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                           QPushButton, QListWidget, QFileDialog, QMessageBox,
                           QListWidgetItem)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QDragEnterEvent, QDropEvent

from interview_corvus.core.file_processor import FileProcessor


class SimpleFileUploadDialog(QDialog):
    """Simple dialog for uploading up to 2 files for processing and saving content to user settings."""
    
    files_uploaded = pyqtSignal(list)  # Signal emitted when files are uploaded successfully
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.selected_files = []
        self.max_files = 2
        self.file_processor = FileProcessor()
        
        self.setWindowTitle("Upload Files")
        self.setMinimumSize(500, 400)
        self.setAcceptDrops(True)
        
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        
        # Title
        title_label = QLabel("📁 Upload Files")
        title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Instructions
        instructions = QLabel(
            f"Upload up to {self.max_files} files. Content will be extracted and saved to user settings.\n"
            "Supported formats: .txt, .md, .py, .js, .html, .css, .json, .xml, .yaml, .yml, .pdf"
        )
        instructions.setStyleSheet("color: #666; margin-bottom: 15px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # File selection button
        select_button = QPushButton("📂 Select Files")
        select_button.setFixedHeight(40)
        select_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        select_button.clicked.connect(self.select_files)
        layout.addWidget(select_button)
        
        # File list
        list_label = QLabel("Selected Files:")
        list_label.setStyleSheet("font-weight: bold; margin-top: 15px;")
        layout.addWidget(list_label)
        
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(150)
        self.file_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        layout.addWidget(self.file_list)
        
        # Clear files button
        clear_button = QPushButton("🗑️ Clear Files")
        clear_button.clicked.connect(self.clear_files)
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        layout.addWidget(clear_button)
        
        # Dialog buttons
        button_layout = QHBoxLayout()
        
        cancel_button = QPushButton("Cancel")
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        button_layout.addStretch()
        
        self.upload_button = QPushButton("Upload & Save")
        self.upload_button.setEnabled(False)
        self.upload_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #219a52;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
            }
        """)
        self.upload_button.clicked.connect(self.upload_files)
        button_layout.addWidget(self.upload_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def select_files(self):
        """Open file dialog to select files."""
        file_paths, _ = QFileDialog.getOpenFileNames(
            self,
            "Select Files",
            "",
            "All Supported (*.txt *.md *.py *.js *.html *.css *.json *.xml *.yaml *.yml *.pdf);;All Files (*)"
        )
        
        if file_paths:
            self.add_files(file_paths)
    
    def add_files(self, file_paths: List[str]):
        """Add files to the selection list."""
        for file_path in file_paths:
            if len(self.selected_files) >= self.max_files:
                QMessageBox.warning(
                    self, 
                    "Maximum Files Reached", 
                    f"You can only upload up to {self.max_files} files."
                )
                break
                
            if file_path not in self.selected_files:
                self.selected_files.append(file_path)
                
                # Add to list widget
                file_name = Path(file_path).name
                item = QListWidgetItem(f"📄 {file_name}")
                item.setData(Qt.ItemDataRole.UserRole, file_path)
                self.file_list.addItem(item)
        
        self.update_upload_button()
    
    def clear_files(self):
        """Clear all selected files."""
        self.selected_files.clear()
        self.file_list.clear()
        self.update_upload_button()
    
    def update_upload_button(self):
        """Update the upload button state."""
        self.upload_button.setEnabled(len(self.selected_files) > 0)
    
    def upload_files(self):
        """Upload files and save content to user settings."""
        if not self.selected_files:
            return
            
        try:
            # Process files and save to user settings
            success = self.file_processor.process_files_and_save(self.selected_files)
            
            if success:
                QMessageBox.information(
                    self,
                    "Upload Successful",
                    f"Successfully uploaded {len(self.selected_files)} files and saved content to user settings."
                )
                self.files_uploaded.emit(self.selected_files)
                self.accept()
            else:
                QMessageBox.warning(
                    self,
                    "Upload Failed",
                    "Failed to process and save files. Please check the logs for details."
                )
                    
        except Exception as e:
            QMessageBox.critical(
                self,
                "Upload Error",
                f"An error occurred while uploading files: {str(e)}"
            )
    
    def dragEnterEvent(self, event: QDragEnterEvent):
        """Handle drag enter events."""
        if event.mimeData().hasUrls():
            event.acceptProposedAction()
    
    def dropEvent(self, event: QDropEvent):
        """Handle drop events."""
        urls = event.mimeData().urls()
        file_paths = []
        
        for url in urls:
            if url.isLocalFile():
                file_paths.append(url.toLocalFile())
        
        if file_paths:
            self.add_files(file_paths)

import os
from pathlib import Path
from typing import List, Optional

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel, 
    QListWidget, QListWidgetItem, QTextEdit, QMessageBox,
    QFileDialog, QProgressBar, QGroupBox, QSplitter
)
from PyQt6.QtCore import Qt, pyqtSignal, QThread
from PyQt6.QtGui import QFont
from loguru import logger

from interview_corvus.core.file_processor import FileProcessor


class FileUploadWorker(QThread):
    """Worker thread for processing uploaded files."""
    
    progress_updated = pyqtSignal(str)  # Progress message
    processing_finished = pyqtSignal(str, list)  # (combined_text, errors)
    processing_failed = pyqtSignal(str)  # Error message
    
    def __init__(self, file_paths: List[str]):
        super().__init__()
        self.file_paths = file_paths
        self.file_processor = FileProcessor()
    
    def run(self):
        """Process files in background thread."""
        try:
            self.progress_updated.emit("Validating files...")
            
            # Validate files
            validation_errors = self.file_processor.validate_files_for_upload(self.file_paths)
            if validation_errors:
                self.processing_failed.emit("Validation failed: " + "; ".join(validation_errors))
                return
            
            self.progress_updated.emit("Processing files...")
            
            # Process files
            combined_text, processing_errors = self.file_processor.process_multiple_files(self.file_paths)
            
            if not combined_text.strip():
                self.processing_failed.emit("No readable content found in the uploaded files")
                return
            
            self.processing_finished.emit(combined_text, processing_errors)
            
        except Exception as e:
            logger.error(f"File processing error: {e}")
            self.processing_failed.emit(f"Processing error: {str(e)}")


class FileUploadDialog(QDialog):
    """Dialog for uploading and processing files for recording analysis."""
    
    files_processed = pyqtSignal(list, str, str)  # (file_paths, combined_text, custom_prompt)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.file_paths = []
        self.combined_text = ""
        self.file_processor = FileProcessor()
        self.processing_worker = None
        
        self.setWindowTitle("Upload Files for Recording Analysis")
        self.setFixedSize(700, 600)
        self.setup_ui()
        
    def setup_ui(self):
        """Set up the dialog UI."""
        layout = QVBoxLayout()
        
        # Title and instructions
        title_label = QLabel("📁 Upload Files for Analysis")
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        instructions = QLabel(
            "Upload up to 2 files (code, docs, PDFs, configs, etc.) for comprehensive analysis.\n"
            "Supported formats: .py, .js, .java, .cpp, .txt, .md, .pdf, .json, .xml, .csv and more."
        )
        instructions.setStyleSheet("color: #7f8c8d; margin-bottom: 15px;")
        instructions.setWordWrap(True)
        layout.addWidget(instructions)
        
        # Main content splitter
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Left side - File selection
        left_widget = QGroupBox("File Selection")
        left_layout = QVBoxLayout()
        
        # Upload button
        upload_button = QPushButton("📂 Select Files")
        upload_button.setFixedHeight(40)
        upload_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """
        )
        upload_button.clicked.connect(self.select_files)
        left_layout.addWidget(upload_button)
        
        # File list
        self.file_list = QListWidget()
        self.file_list.setMaximumHeight(150)
        self.file_list.setStyleSheet("""
            QListWidget {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                background-color: #f8f9fa;
            }
            QListWidget::item {
                padding: 8px;
                border-bottom: 1px solid #ecf0f1;
            }
            QListWidget::item:selected {
                background-color: #3498db;
                color: white;
            }
        """)
        left_layout.addWidget(QLabel("Selected Files:"))
        left_layout.addWidget(self.file_list)
        
        # Clear files button
        clear_button = QPushButton("🗑️ Clear Files")
        clear_button.clicked.connect(self.clear_files)
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        left_layout.addWidget(clear_button)
        
        left_widget.setLayout(left_layout)
        splitter.addWidget(left_widget)
        
        # Right side - Custom prompt
        right_widget = QGroupBox("Custom Prompt (Optional)")
        right_layout = QVBoxLayout()
        
        prompt_instructions = QLabel(
            "Add custom instructions for analyzing the files:"
        )
        prompt_instructions.setStyleSheet("color: #7f8c8d; margin-bottom: 5px;")
        right_layout.addWidget(prompt_instructions)
        
        self.prompt_text = QTextEdit()
        self.prompt_text.setPlaceholderText(
            "e.g., 'Focus on security vulnerabilities and performance issues'\n"
            "or 'Explain this code for a beginner developer'\n"
            "or leave empty for general analysis..."
        )
        self.prompt_text.setMaximumHeight(120)
        font = QFont("Monaco", 10)
        if not font.exactMatch():
            font = QFont("Consolas", 10)
        self.prompt_text.setFont(font)
        right_layout.addWidget(self.prompt_text)
        
        right_widget.setLayout(right_layout)
        splitter.addWidget(right_widget)
        
        # Set splitter proportions
        splitter.setSizes([350, 350])
        layout.addWidget(splitter)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #bdc3c7;
                border-radius: 4px;
                text-align: center;
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 3px;
            }
        """)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #7f8c8d; font-style: italic;")
        layout.addWidget(self.status_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        button_layout.addStretch()
        
        process_button = QPushButton("🚀 Process & Analyze")
        process_button.setFixedSize(150, 40)
        process_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 6px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
            QPushButton:disabled {
                background-color: #95a5a6;
                color: #7f8c8d;
            }
        """)
        process_button.clicked.connect(self.process_files)
        process_button.setEnabled(False)
        self.process_button = process_button
        button_layout.addWidget(process_button)
        
        cancel_button = QPushButton("Cancel")
        cancel_button.setFixedSize(80, 40)
        cancel_button.clicked.connect(self.reject)
        button_layout.addWidget(cancel_button)
        
        layout.addLayout(button_layout)
        self.setLayout(layout)
        
    def select_files(self):
        """Open file dialog to select files."""
        file_dialog = QFileDialog()
        file_dialog.setFileMode(QFileDialog.FileMode.ExistingFiles)
        file_dialog.setNameFilter(
            "All Supported (*.py *.js *.ts *.java *.cpp *.c *.h *.cs *.go *.rs *.rb *.php "
            "*.html *.css *.json *.xml *.yaml *.yml *.txt *.md *.pdf *.csv *.log *.conf);;"
            "Code Files (*.py *.js *.ts *.java *.cpp *.c *.h *.cs *.go *.rs *.rb *.php);;"
            "Document Files (*.pdf *.txt *.md *.csv *.log);;"
            "Web Files (*.html *.css *.json *.xml *.yaml *.yml);;"
            "Text Files (*.txt *.md *.csv *.log *.conf);;"
            "All Files (*)"
        )
        
        if file_dialog.exec() == QFileDialog.DialogCode.Accepted:
            selected_files = file_dialog.selectedFiles()
            
            if len(selected_files) > 2:
                QMessageBox.warning(
                    self, 
                    "Too Many Files",
                    f"You can only upload up to 2 files at a time.\n"
                    f"You selected {len(selected_files)} files."
                )
                return
            
            self.file_paths = selected_files
            self.update_file_list()
            
    def update_file_list(self):
        """Update the file list display."""
        self.file_list.clear()
        
        for file_path in self.file_paths:
            file_info = self.file_processor.get_file_info(file_path)
            
            # Create list item
            item_text = f"{file_info['name']} ({file_info['size_mb']} MB)"
            if not file_info['is_supported']:
                item_text += " ⚠️ Unsupported"
            if 'error' in file_info:
                item_text += " ❌ Error"
                
            item = QListWidgetItem(item_text)
            
            # Color coding
            if 'error' in file_info:
                item.setForeground(Qt.GlobalColor.red)
            elif not file_info['is_supported']:
                item.setForeground(Qt.GlobalColor.darkYellow)
            else:
                item.setForeground(Qt.GlobalColor.darkGreen)
                
            self.file_list.addItem(item)
        
        # Update process button state
        has_valid_files = any(
            self.file_processor.get_file_info(fp)['is_supported'] and 
            'error' not in self.file_processor.get_file_info(fp)
            for fp in self.file_paths
        )
        self.process_button.setEnabled(has_valid_files)
        
        # Update status
        if self.file_paths:
            valid_count = sum(1 for fp in self.file_paths 
                            if self.file_processor.get_file_info(fp)['is_supported'])
            self.status_label.setText(f"{valid_count}/{len(self.file_paths)} files are supported")
        else:
            self.status_label.setText("No files selected")
            
    def clear_files(self):
        """Clear all selected files."""
        self.file_paths.clear()
        self.update_file_list()
        
    def process_files(self):
        """Process the selected files."""
        if not self.file_paths:
            QMessageBox.warning(self, "No Files", "Please select files to process.")
            return
            
        # Show progress
        self.progress_bar.setVisible(True)
        self.progress_bar.setRange(0, 0)  # Indeterminate progress
        self.status_label.setText("Processing files...")
        self.process_button.setEnabled(False)
        
        # Start processing in background thread
        self.processing_worker = FileUploadWorker(self.file_paths)
        self.processing_worker.progress_updated.connect(self.update_progress)
        self.processing_worker.processing_finished.connect(self.on_processing_finished)
        self.processing_worker.processing_failed.connect(self.on_processing_failed)
        self.processing_worker.start()
        
    def update_progress(self, message: str):
        """Update progress display."""
        self.status_label.setText(message)
        
    def on_processing_finished(self, combined_text: str, errors: List[str]):
        """Handle successful file processing."""
        self.progress_bar.setVisible(False)
        self.process_button.setEnabled(True)
        
        if errors:
            warning_msg = "Files processed with warnings:\n" + "\n".join(errors)
            QMessageBox.information(self, "Processing Warnings", warning_msg)
        
        # Get custom prompt
        custom_prompt = self.prompt_text.toPlainText().strip()
        
        # Emit signal and close dialog
        self.files_processed.emit(self.file_paths, combined_text, custom_prompt)
        self.accept()
        
    def on_processing_failed(self, error_message: str):
        """Handle processing failure."""
        self.progress_bar.setVisible(False)
        self.process_button.setEnabled(True)
        self.status_label.setText("Processing failed")
        
        QMessageBox.critical(self, "Processing Error", f"Failed to process files:\n\n{error_message}")
        
    def closeEvent(self, event):
        """Handle dialog close event."""
        if self.processing_worker and self.processing_worker.isRunning():
            self.processing_worker.quit()
            self.processing_worker.wait()
        event.accept()
