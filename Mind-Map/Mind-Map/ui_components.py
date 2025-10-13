import PySide6.QtCore

from PySide6.QtGui import (QTextCursor, QPainter, QColor, QFont, QKeySequence, 
                           QImage, QAction, QIcon, QPen)
from PySide6.QtWidgets import (QWidget, QVBoxLayout, QTextEdit, QPushButton,
                              QHBoxLayout, QLabel, QSplitter, QFileDialog, QMenu,
                              QMessageBox, QToolBar, QLineEdit, QGridLayout,
                              QSizePolicy, QStyle, QSizeGrip, QToolButton)
from PySide6.QtCore import Qt, QPointF, Signal, QTimer, QEvent, QRectF

from app_utils import StyleSheet, AIWorker, IconFactory
from graphics_items import MindMapView

class LoadingIndicator(QWidget):
    """A simple, animated spinning indicator for loading states."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.angle = 0
        self.timer = QTimer(self)
        self.timer.timeout.connect(self.update_angle)
        self.timer.setInterval(20)
        self.setFixedSize(16, 16)
        self.hide()

    def update_angle(self):
        self.angle = (self.angle + 10) % 360
        self.update()

    def paintEvent(self, event):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        pen_color = self.palette().color(self.parent().foregroundRole())
        pen = QPen(pen_color, 2)
        pen.setCapStyle(Qt.RoundCap)
        painter.setPen(pen)
        
        painter.drawArc(self.rect().adjusted(2, 2, -2, -2), self.angle * 16, 90 * 16)

    def startAnimation(self):
        self.show()
        self.timer.start()

    def stopAnimation(self):
        self.timer.stop()
        self.hide()

class EditorPanel(QWidget):
    """Panel for editing markdown text, with real-time updates via debounce timer."""
    renderRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("EditorPanel")
        self.setSizePolicy(QSizePolicy.Fixed, QSizePolicy.Preferred)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # --- Unified Command Toolbar ---
        self.toolbar = QToolBar()
        self.toolbar.setObjectName("MainToolbar")
        self.toolbar.setIconSize(PySide6.QtCore.QSize(18, 18))
        self.toolbar.setContentsMargins(0, 0, 0, 0)
        
        # --- Actions with Icons ---
        self.new_action = QAction("New", self)
        self.new_action.setShortcut(QKeySequence.New)
        
        self.open_action = QAction("Open", self)
        self.open_action.setShortcut(QKeySequence.Open)
        
        self.save_action = QAction("Save", self)
        self.save_action.setShortcut(QKeySequence.Save)
        
        self.render_action = QAction("Render", self)
        self.render_action.setShortcut("Ctrl+R")
        self.render_action.setToolTip("Render Mind Map (Ctrl+R)")
        
        self.enhance_action = QAction("AI Enhance", self)
        self.enhance_action.setShortcut("Ctrl+E")
        self.enhance_action.setToolTip("Enhance with AI (Ctrl+E)")
        
        self.export_action = QAction("Export", self)
        self.export_action.setShortcut("Ctrl+Shift+E")
        self.export_action.setToolTip("Export as PNG (Ctrl+Shift+E)")
        
        self.fit_view_action = QAction("Fit All", self)
        self.fit_view_action.setShortcut("Home")
        
        self.zoom_selection_action = QAction("Zoom Selection", self)
        self.zoom_selection_action.setShortcut("F")
        
        self.theme_toggle_action = QAction("Dark Theme", self)
        self.theme_toggle_action.setToolTip("Enable/Disable Dark Theme")
        self.theme_toggle_action.setCheckable(True)

        # --- Add Actions to Toolbar ---
        self.toolbar.addAction(self.new_action)
        self.toolbar.addAction(self.open_action)
        self.toolbar.addAction(self.save_action)
        self.toolbar.addSeparator()
        
        self.toolbar.addAction(self.render_action)
        self.toolbar.addAction(self.enhance_action)
        self.toolbar.addSeparator()
        
        self.toolbar.addAction(self.export_action)
        
        # View menu button
        self.view_button = QToolButton(self)
        self.view_button.setText("☰")
        self.view_button.setToolTip("View Options")
        view_menu = QMenu(self)
        view_menu.addAction(self.fit_view_action)
        view_menu.addAction(self.zoom_selection_action)
        view_menu.addSeparator()
        view_menu.addAction(self.theme_toggle_action)
        self.view_button.setMenu(view_menu)
        self.view_button.setPopupMode(QToolButton.InstantPopup)
        self.toolbar.addWidget(self.view_button)
        
        # --- Right Side: Search and Theme ---
        spacer = QWidget()
        spacer.setSizePolicy(QSizePolicy.Expanding, QSizePolicy.Preferred)
        

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("🔍 Search nodes...")
        self.search_box.setMaximumWidth(200)
        self.search_box.setContentsMargins(0, 0, 0, 0)
        self.search_box.textChanged.connect(self.search_nodes)
        self.toolbar.addWidget(self.search_box)
        
        layout.addWidget(self.toolbar)
        
        # --- Text Editor ---
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Consolas", 11))
        layout.addWidget(self.text_edit, 1)
        
        # --- Breadcrumb/Status Bar ---
        self.status_bar = QWidget()
        self.status_bar.setObjectName("StatusBar")
        status_layout = QHBoxLayout(self.status_bar)
        status_layout.setContentsMargins(0, 0, 10, 0)
        status_layout.setSpacing(10)

        self.breadcrumb_label = QLabel("No node selected")
        self.breadcrumb_label.setObjectName("BreadcrumbLabel")
        
        self.loading_indicator = LoadingIndicator(self)
        
        status_layout.addWidget(self.breadcrumb_label, 1)
        status_layout.addWidget(self.loading_indicator)
        
        layout.addWidget(self.status_bar)

        # --- Timers and Connections ---
        self.render_debounce_timer = QTimer(self)
        self.render_debounce_timer.setSingleShot(True)
        self.render_debounce_timer.setInterval(750)
        self.render_debounce_timer.timeout.connect(self.request_render)

        self.text_edit.textChanged.connect(self.on_text_changed)
        self.mind_map_view = None

    def update_icons(self, icon_color: QColor):
        """Updates all toolbar icons with a specific color."""
        self.new_action.setIcon(IconFactory.create_icon("new", icon_color))
        self.open_action.setIcon(IconFactory.create_icon("open", icon_color))
        self.save_action.setIcon(IconFactory.create_icon("save", icon_color))
        self.render_action.setIcon(IconFactory.create_icon("render", icon_color))
        self.enhance_action.setIcon(IconFactory.create_icon("enhance", icon_color))
        self.export_action.setIcon(IconFactory.create_icon("export", icon_color))

    def on_text_changed(self): 
        self.render_debounce_timer.start()
        
    def request_render(self): 
        self.renderRequested.emit()
        
    def search_nodes(self, text):
        if self.mind_map_view: 
            self.mind_map_view.scene().search_nodes(text)

class TitleBar(QWidget):
    """custom title bar with standard icons and behavior."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("TitleBar")
        self.setFixedHeight(30)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 0, 0)
        layout.setSpacing(0)

        self.title = QLabel("Mind Map Editor")
        self.title.setObjectName("TitleBarLabel")
        
        layout.addWidget(self.title)
        layout.addStretch()

        self.min_btn = QPushButton()
        self.min_btn.setObjectName("MinButton")
        self.min_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMinButton))
        self.min_btn.clicked.connect(self.window().showMinimized)

        self.max_btn = QPushButton()
        self.max_btn.setObjectName("MaxButton")
        self.max_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton))
        self.max_btn.clicked.connect(self.toggle_max)

        self.close_btn = QPushButton()
        self.close_btn.setObjectName("CloseButton")
        self.close_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton))
        self.close_btn.clicked.connect(self.window().close)

        buttons = [self.min_btn, self.max_btn, self.close_btn]
        for btn in buttons:
            btn.setFixedSize(45, 30)
            btn.setIconSize(PySide6.QtCore.QSize(16, 16)) 
            layout.addWidget(btn)

        self.drag_pos = QPointF()

    def update_maximize_button_icon(self):
        """Updates the maximize button icon based on window state."""
        if self.window().isMaximized():
            self.max_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarNormalButton))
        else:
            self.max_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton))

    def toggle_max(self):
        """Toggles between maximized and normal window state."""
        if self.window().isMaximized():
            self.window().showNormal()
        else:
            self.window().showMaximized()
        self.update_maximize_button_icon()

    def mousePressEvent(self, event):
        """Records drag position for window movement."""
        if event.button() == Qt.LeftButton and not self.window().isMaximized():
             self.drag_pos = event.globalPosition() - self.window().frameGeometry().topLeft()

    def mouseMoveEvent(self, event):
        """Moves the window during drag."""
        if event.buttons() == Qt.LeftButton and not self.window().isMaximized():
            self.window().move((event.globalPosition() - self.drag_pos).toPoint())

    def mouseDoubleClickEvent(self, event):
        """Toggle maximize on double-click."""
        if event.button() == Qt.LeftButton:
            self.toggle_max()

class MainWindow(QWidget):
    """Main application window with custom title bar, editor, and mind map view."""
    def __init__(self):
        super().__init__()
        self.is_dark_theme = True
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(100, 100, 1600, 900)
        
        self.setStyleSheet("background-color: #3f3f3f;")

        main_layout = QGridLayout()
        main_layout.setContentsMargins(1, 1, 1, 1)
        main_layout.setSpacing(0)

        self.container_widget = QWidget()
        self.container_widget.setObjectName("MainWindowContainer")
        container_layout = QVBoxLayout(self.container_widget)
        container_layout.setContentsMargins(0, 0, 0, 0)
        container_layout.setSpacing(0)

        self.title_bar = TitleBar(self)
        
        splitter = QSplitter(Qt.Horizontal)
        
        self.editor_panel = EditorPanel()
        
        self.mind_map_view = MindMapView()
        
        splitter.addWidget(self.editor_panel)
        splitter.addWidget(self.mind_map_view)
        
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        

        container_layout.addWidget(self.title_bar)
        container_layout.addWidget(splitter)
        
        main_layout.addWidget(self.container_widget, 0, 0)

        size_grip = QSizeGrip(self)
        main_layout.addWidget(size_grip, 0, 0, Qt.AlignBottom | Qt.AlignRight)
        
        self.setLayout(main_layout)

        self.setWindowTitle("Mind Map Editor")
        self.editor_panel.mind_map_view = self.mind_map_view
        
        self.current_file = None
        self.ai_worker = None
        self.original_breadcrumb_text = ""
        self.setup_connections()
        self.editor_panel.theme_toggle_action.setChecked(self.is_dark_theme)
        self.apply_theme()
        self.load_example_content()

    def apply_theme(self):
        if self.is_dark_theme:
            self.container_widget.setStyleSheet(StyleSheet.DARK_THEME)
            self.mind_map_view.scene().setBackgroundBrush(QColor("#2a2a2a"))
            self.setStyleSheet("background-color: #3f3f3f;")
            icon_color = QColor("#d4d4d4")
        else:
            self.container_widget.setStyleSheet(StyleSheet.LIGHT_THEME)
            self.mind_map_view.scene().setBackgroundBrush(QColor("#ffffff"))
            self.setStyleSheet("background-color: #cccccc;")
            icon_color = QColor("#1e1e1e")
        
        self.editor_panel.update_icons(icon_color)
        self.mind_map_view.set_theme(self.is_dark_theme)

    def toggle_theme(self):
        self.is_dark_theme = self.editor_panel.theme_toggle_action.isChecked()
        self.apply_theme()

    def changeEvent(self, event):
        """Handle window state changes to update the maximize button icon."""
        if event.type() == QEvent.Type.WindowStateChange:
            self.title_bar.update_maximize_button_icon()
        super().changeEvent(event)
        
    def setWindowTitle(self, title):
        super().setWindowTitle(title)
        self.title_bar.title.setText(title)

    def setup_connections(self):
        """Sets up signal-slot connections for actions and buttons."""
        self.editor_panel.render_action.triggered.connect(self.render_markdown)
        self.editor_panel.export_action.triggered.connect(self.export_mind_map)
        self.editor_panel.new_action.triggered.connect(self.new_file)
        self.editor_panel.open_action.triggered.connect(self.open_file)
        self.editor_panel.save_action.triggered.connect(self.save_file)
        self.editor_panel.enhance_action.triggered.connect(self.enhance_with_ai)
        self.editor_panel.renderRequested.connect(self.render_markdown)
        self.mind_map_view.scene().nodeSelected.connect(self.handle_node_selection)
        self.editor_panel.fit_view_action.triggered.connect(self.fit_view)
        self.editor_panel.zoom_selection_action.triggered.connect(self.zoom_to_selection)
        self.editor_panel.theme_toggle_action.triggered.connect(self.toggle_theme)

    def fit_view(self):
        if self.mind_map_view.scene().items():
            self.mind_map_view.fitInView(self.mind_map_view.scene().itemsBoundingRect(), Qt.KeepAspectRatio)
    
    def zoom_to_selection(self):
        selected_items = self.mind_map_view.scene().selectedItems()
        if not selected_items: return
        bounding_rect = QRectF()
        for item in selected_items: bounding_rect = bounding_rect.united(item.sceneBoundingRect())
        self.mind_map_view.fitInView(bounding_rect, Qt.KeepAspectRatio)
    
    def enhance_with_ai(self):
        raw_text = self.editor_panel.text_edit.toPlainText().strip()
        if not raw_text:
            QMessageBox.warning(self, "Input Required", "Please enter some text to enhance.")
            return
            
        self.editor_panel.enhance_action.setEnabled(False)
        self.editor_panel.render_action.setEnabled(False)

        self.original_breadcrumb_text = self.editor_panel.breadcrumb_label.text()
        self.editor_panel.breadcrumb_label.setText("Enhancing with AI...")
        self.editor_panel.loading_indicator.startAnimation()
        
        self.ai_worker = AIWorker(raw_text)
        self.ai_worker.finished.connect(self.handle_ai_result)
        self.ai_worker.error.connect(self.handle_ai_error)
        self.ai_worker.start()

    def handle_ai_result(self, markdown_text):
        self.editor_panel.text_edit.textChanged.disconnect(self.editor_panel.on_text_changed)
        self.editor_panel.text_edit.setText( markdown_text)
        self.editor_panel.text_edit.textChanged.connect(self.editor_panel.on_text_changed)
        self.render_markdown()
        self.reset_ai_button_state()

    def handle_ai_error(self, error_message):
        QMessageBox.critical(self, "AI Error", error_message)
        self.reset_ai_button_state()

    def reset_ai_button_state(self):
        self.editor_panel.enhance_action.setEnabled(True)
        self.editor_panel.render_action.setEnabled(True)
        self.editor_panel.loading_indicator.stopAnimation()
        self.editor_panel.breadcrumb_label.setText(self.original_breadcrumb_text)

    def load_example_content(self):
        example_text = """# Mind Map Tutorial
## Getting Started
### Create Nodes using Markdown headings. The more hashtags, the deeper the node level.
### Navigate Map by clicking and dragging the background. Use Ctrl + Mouse Wheel to zoom in and out.
## Features
### Auto-rendering
### Export Options
### AI Enhancement
#### Structure raw text from your notes, a document, or any copied text.
#### Create mind maps from meeting notes to visualize key topics and action items.
## Tips
### Keyboard Shortcuts like Ctrl+R to manually render or Ctrl+E to use the AI enhancement.
### Markdown Syntax"""
        self.editor_panel.text_edit.setText(example_text)
        self.render_markdown()

    def new_file(self):
        if self.maybe_save():
            self.editor_panel.text_edit.clear()
            self.mind_map_view.scene().clear_nodes()
            self.current_file = None
            self.setWindowTitle("Mind Map Editor - New File")

    def open_file(self):
        if self.maybe_save():
            file_name, _ = QFileDialog.getOpenFileName(self, "Open Mind Map", "", "Markdown Files (*.md);;All Files (*)")
            if file_name: self.load_file(file_name)

    def save_file(self):
        if not self.current_file: return self.save_file_as()
        return self.save_file_at(self.current_file)

    def save_file_as(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Save Mind Map", "", "Markdown Files (*.md);;All Files (*)")
        if file_name: return self.save_file_at(file_name)
        return False

    def save_file_at(self, file_name):
        try:
            with open(file_name, 'w', encoding='utf-8') as file:
                file.write(self.editor_panel.text_edit.toPlainText())
            self.current_file = file_name
            self.setWindowTitle(f"Mind Map Editor - {file_name}")
            return True
        except Exception as e:
            QMessageBox.warning(self, "Save Error", f"Failed to save file: {str(e)}")
            return False

    def load_file(self, file_name):
        try:
            with open(file_name, 'r', encoding='utf-8') as file: content = file.read()
            self.editor_panel.text_edit.setText(content)
            self.current_file = file_name
            self.setWindowTitle(f"Mind Map Editor - {file_name}")
            self.render_markdown()
            return True
        except Exception as e:
            QMessageBox.warning(self, "Load Error", f"Failed to load file: {str(e)}")
            return False

    def maybe_save(self):
        if not self.editor_panel.text_edit.document().isModified(): return True
        ret = QMessageBox.warning(self, "Mind Map", "The document has been modified.\nDo you want to save your changes?", QMessageBox.Save | QMessageBox.Discard | QMessageBox.Cancel)
        if ret == QMessageBox.Save: return self.save_file()
        elif ret == QMessageBox.Cancel: return False
        return True

    def export_mind_map(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export as PNG", "", "PNG Files (*.png)")
        if not file_name:
            return
        self.export_as_png(file_name)


    def export_as_png(self, file_name):
        scene = self.mind_map_view.scene()
        if not scene.items():
            QMessageBox.information(self, "Export Aborted", "Cannot export an empty mind map.")
            return
            
        scene_rect = scene.itemsBoundingRect()
        
        image = QImage(scene_rect.size().toSize(), QImage.Format_ARGB32)
        image.fill(Qt.transparent)
        
        painter = QPainter(image)
        painter.setRenderHint(QPainter.Antialiasing)
        
        painter.translate(-scene_rect.topLeft())
        
        scene.render(painter)
        painter.end()
        
        image.save(file_name)
        QMessageBox.information(self, "Export Successful", f"Mind map exported to {file_name}")

    def handle_node_selection(self, node):
        if node:
            path = []; curr = node
            while curr: path.append(curr.text); curr = curr.parent
            breadcrumb_text = " > ".join(reversed(path))
        else:
            breadcrumb_text = "No node selected"

        # Only update if AI is not running
        if not self.editor_panel.loading_indicator.isVisible():
            self.editor_panel.breadcrumb_label.setText(breadcrumb_text)
        self.original_breadcrumb_text = breadcrumb_text

    def render_markdown(self):
        markdown_text = self.editor_panel.text_edit.toPlainText()
        self.mind_map_view.parse_and_render_markdown(markdown_text)
        self.fit_view()