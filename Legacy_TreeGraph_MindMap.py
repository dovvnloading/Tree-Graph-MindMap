# Legacy Code - this is now outdated and here for QoL. See the main 'Mind-Map' file for the source code/project file

import sys
import ollama
import PySide6.QtCore

from PySide6.QtGui import QTextCursor, QPainterPath, QPainter, QPen, QColor, QBrush, QFont, QKeySequence, QImage, QAction, QIcon
from PySide6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QTextEdit, QPushButton, QGraphicsScene, QGraphicsView,
                              QHBoxLayout, QGraphicsItem, QColorDialog, QLabel,
                              QFrame, QSplitter, QFileDialog, QMenu, QMessageBox,
                              QToolBar, QLineEdit, QGraphicsPathItem, QGridLayout,
                              QSizePolicy, QStyle, QSizeGrip)
from PySide6.QtCore import (Qt, QRectF, QPointF, Signal, QTimer, QThread, QEvent)

# --- AI Enhancement System Prompt and Worker ---

AI_MARKDOWN_SYSTEM_PROMPT = """
You are an expert data analyst and information architect. Your task is to transform raw, unstructured text into a well-structured, hierarchical Markdown document. This output is specifically intended to be parsed and visualized as a node-based mind map or infographic.

## YOUR GOAL
- Identify the central theme or root topic of the text. This will be the main `#` heading.
- Extract key sub-topics or categories. These will be `##` headings.
- Find supporting details, points, or sub-categories for each sub-topic. These will be `###` headings, `####` headings, and so on.
- Organize the information logically to show relationships and hierarchy clearly.
- Condense lengthy sentences into concise node titles.

## CRITICAL RULES
- **MUST** output **ONLY** the Markdown text.
- **DO NOT** include any explanations, introductions, summaries, or concluding remarks like "Here is the Markdown..." or "This structure helps visualize...".
- The entire output must be valid Markdown, starting with a single level 1 heading (`#`).
- Use deeper heading levels (`###`, `####`) to represent finer details.
- Maintain the core information and intent of the original text.

## EXAMPLE
User Text: "Our company project, Phoenix, is running behind. The UI/UX team is blocked because the backend APIs are not ready. Specifically, the authentication endpoint is down, and the user profile service is returning 500 errors. On the frontend side, the component library needs to be updated to version 3.1, which is a breaking change."

Your Markdown Output:
# Project Phoenix Status
## Backend Issues
### API Readiness
#### Authentication Endpoint Down
#### User Profile Service 500 Errors
## Frontend Issues
### UI/UX Team Blocked
### Component Library Update
#### Requires upgrade to v3.1
#### Breaking Changes Expected
"""

class AIWorker(QThread):
    """Worker thread to process text with Ollama without freezing the UI."""
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, text_to_process, model='phi4:14b'):
        super().__init__()
        self.text = text_to_process
        self.model = model

    def run(self):
        try:
            messages = [
                {'role': 'system', 'content': AI_MARKDOWN_SYSTEM_PROMPT},
                {'role': 'user', 'content': self.text}
            ]
            
            response = ollama.chat(model=self.model, messages=messages)
            
            if 'message' in response and 'content' in response['message']:
                self.finished.emit(response['message']['content'])
            else:
                self.error.emit("Received an invalid response from the AI model.")
        
        except Exception as e:
            error_msg = str(e)
            if "could not connect to ollama" in error_msg.lower() or "connection refused" in error_msg.lower():
                self.error.emit("Connection Error: Could not connect to Ollama. Please ensure the Ollama service is running on your system.")
            else:
                self.error.emit(f"An AI processing error occurred: {error_msg}")

class StyleSheet:
    """Defines the dark theme stylesheet for the application."""
    DARK_THEME = """
        QMainWindow, QWidget {
            background-color: #1e1e1e;
            color: #ffffff;
        }
        QTextEdit {
            background-color: #252526;
            color: #d4d4d4;
            border: 1px solid #3f3f3f;
            border-radius: 4px;
            padding: 8px;
            selection-background-color: #264f78;
            font-family: 'Consolas', monospace;
        }
        QPushButton {
            background-color: #0e639c;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            min-height: 30px; 
        }
        QPushButton:hover {
            background-color: #1177bb;
        }
        QPushButton:pressed {
            background-color: #0d5485;
        }
        QPushButton:disabled {
            background-color: #2d3e49;
            color: #7b8a93;
        }
        QGraphicsView {
            background-color: #252526;
            border: 1px solid #3f3f3f;
            border-radius: 4px;
        }
        QLabel {
            color: #d4d4d4;
            font-weight: bold;
        }
        #BreadcrumbLabel {
            color: #9e9e9e;
            font-weight: normal;
            font-size: 9pt;
            padding: 4px;
            background-color: #252526;
            border-top: 1px solid #3f3f3f;
        }
        QSplitter::handle {
            background-color: #3f3f3f;
        }
        QFrame {
            background-color: #252526;
            border: 1px solid #3f3f3f;
            border-radius: 4px;
        }
        QToolBar {
            background-color: #333333;
            border: none;
            spacing: 4px;
            padding: 4px;
        }
        QToolBar QToolButton {
            background-color: transparent;
            border: none;
            border-radius: 4px;
            padding: 4px;
        }
        QToolBar QToolButton:hover {
            background-color: #404040;
        }
        QMenu {
            background-color: #252526;
            border: 1px solid #3f3f3f;
        }
        QMenu::item {
            padding: 6px 24px;
            color: #d4d4d4;
        }
        QMenu::item:selected {
            background-color: #0e639c;
        }
        QLineEdit {
            background-color: #252526;
            color: #d4d4d4;
            border: 1px solid #3f3f3f;
            border-radius: 4px;
            padding: 4px 8px;
        }
    """

class Connection(QGraphicsPathItem):
    """Represents a dynamic connection line between two nodes in the mind map."""
    def __init__(self, start_node, end_node):
        super().__init__()
        self.start_node = start_node
        self.end_node = end_node
        self.setPen(QPen(QColor("#666666"), 2, Qt.SolidLine, Qt.RoundCap, Qt.RoundJoin))
        self.update_path()

    def update_path(self):
        """Recalculates and sets the cubic Bezier path based on current node positions."""
        start_point = self.start_node.get_output_point()
        end_point = self.end_node.get_input_point()
        
        path = QPainterPath()
        path.moveTo(start_point)
        
        ctrl1_x = start_point.x() + (end_point.x() - start_point.x()) * 0.5
        ctrl1_y = start_point.y()
        ctrl2_x = ctrl1_x
        ctrl2_y = end_point.y()
        
        path.cubicTo(QPointF(ctrl1_x, ctrl1_y), QPointF(ctrl2_x, ctrl2_y), end_point)
        self.setPath(path)

class RoundedRectItem(QGraphicsItem):
    """Custom graphics item representing a node as a rounded rectangle."""
    def __init__(self, x, y, width, height, radius=20, color="#3498db"):
        super().__init__()
        self.rect = QRectF(0, 0, width, height)
        self.radius = radius
        self.color = QColor(color)
        self.setPos(x, y)
        self.setAcceptHoverEvents(True)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)
        self.hovered = False
        self.collapsed = False
        self.collapse_button_rect = QRectF(width - 20, height/2 - 10, 20, 20)
        self.node = None

    def boundingRect(self):
        return self.rect.adjusted(-2, -2, 2, 2)

    def paint(self, painter, option, widget=None):
        painter.setRenderHint(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 0, 0, 50))
        shadow_path = QPainterPath()
        shadow_path.addRoundedRect(self.rect.translated(2, 2), self.radius, self.radius)
        painter.drawPath(shadow_path)

        path = QPainterPath()
        path.addRoundedRect(self.rect, self.radius, self.radius)
        
        if self.isSelected():
            painter.setPen(QPen(QColor("#ffffff"), 2))
        elif self.hovered:
            painter.setPen(QPen(QColor("#888888")))
        else:
            painter.setPen(QPen(QColor("#555555")))
            
        painter.setBrush(QBrush(self.color))
        painter.drawPath(path)

        if self.node and self.node.children:
            painter.setPen(QPen(QColor("#ffffff")))
            painter.drawRect(self.collapse_button_rect)
            painter.drawText(self.collapse_button_rect, 
                           Qt.AlignCenter, 
                           "-" if not self.collapsed else "+")

    def toggle_collapse(self):
        """Toggles the collapsed state and triggers the node's update logic."""
        if self.node and self.node.children:
            self.collapsed = not self.collapsed
            self.node.toggle_children(self.collapsed)
            self.update()

    def mousePressEvent(self, event):
        if self.node and self.node.children and self.collapse_button_rect.contains(event.pos()):
            self.toggle_collapse()
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if event.button() == Qt.LeftButton:
            color = QColorDialog.getColor(initial=self.color)
            if color.isValid():
                self.color = color
                self.update()
        super().mouseDoubleClickEvent(event)

    def hoverEnterEvent(self, event):
        self.hovered = True
        self.update()

    def hoverLeaveEvent(self, event):
        self.hovered = False
        self.update()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange and self.scene() and self.node:
            self.node.x = value.x()
            self.node.y = value.y()
            
            if self.node.incoming_connection:
                self.node.incoming_connection.update_path()
            for conn in self.node.outgoing_connections:
                conn.update_path()
            
            self.scene().update()
        
        return super().itemChange(change, value)

class Node:
    """Represents a node in the mind map hierarchy."""
    WIDTH = 200
    HEIGHT = 50
    HORIZONTAL_SPACING = 300
    VERTICAL_SPACING = 100
    
    def __init__(self, text, x, y, color="#3498db"):
        self.text = text
        self.x = x
        self.y = y
        self.width = self.WIDTH
        self.height = self.HEIGHT
        self.color = color
        self.parent = None
        self.children = []
        self.outgoing_connections = []
        self.incoming_connection = None
        self.rect_item = None
        self.text_item = None
        self.visible = True
        
    def get_input_point(self):
        return QPointF(self.x, self.y + self.height / 2)
        
    def get_output_point(self):
        return QPointF(self.x + self.width, self.y + self.height / 2)

    def toggle_children(self, collapsed):
        """Recursively updates the visibility of all descendant nodes."""
        for child in self.children:
            is_visible = not collapsed
            
            child.visible = is_visible
            if child.rect_item:
                child.rect_item.setVisible(is_visible)
            if child.incoming_connection:
                child.incoming_connection.setVisible(is_visible)

            child_should_hide_its_children = (not is_visible) or child.rect_item.collapsed
            child.toggle_children(child_should_hide_its_children)

class MindMapScene(QGraphicsScene):
    """Custom scene for managing mind map nodes and connections."""
    nodeSelected = Signal(object)
    
    def __init__(self):
        super().__init__()
        self.nodes = []
        self.level_counts = {}
        self.setBackgroundBrush(QColor("#252526"))
        self.selected_node = None
        
    def clear_nodes(self):
        self.clear()
        self.nodes = []
        self.level_counts = {}
        self.selected_node = None
        self.nodeSelected.emit(None)
        
    def mousePressEvent(self, event):
        item = self.itemAt(event.scenePos(), self.views()[0].transform())
        if isinstance(item, RoundedRectItem):
            if self.selected_node:
                self.selected_node.rect_item.setSelected(False)
            self.selected_node = next((node for node in self.nodes if node.rect_item == item), None)
            if self.selected_node:
                item.setSelected(True)
                self.nodeSelected.emit(self.selected_node)
        super().mousePressEvent(event)

    def add_node(self, node, parent=None):
        """Adds a node with dynamic height and correctly parented text."""
        
        temp_text_item = self.addText(node.text, QFont("Segoe UI", 10))
        padding = 20
        temp_text_item.setTextWidth(node.width - padding)
        
        text_height = temp_text_item.boundingRect().height()
        node.height = max(Node.HEIGHT, text_height + padding)
        
        self.removeItem(temp_text_item)
        
        node.rect_item = RoundedRectItem(node.x, node.y, node.width, node.height, color=node.color)
        node.rect_item.node = node
        
        node.text_item = self.addText(node.text, QFont("Segoe UI", 10))
        node.text_item.setDefaultTextColor(QColor("#ffffff"))
        node.text_item.setTextWidth(node.width - padding)
        node.text_item.setParentItem(node.rect_item)
        
        text_x = (node.width - node.text_item.boundingRect().width()) / 2
        text_y = (node.height - node.text_item.boundingRect().height()) / 2
        node.text_item.setPos(text_x, text_y)

        self.addItem(node.rect_item)
        
        if parent:
            parent.children.append(node)
            node.parent = parent
            conn = Connection(parent, node)
            self.addItem(conn)
            parent.outgoing_connections.append(conn)
            node.incoming_connection = conn
            
        self.nodes.append(node)

    def search_nodes(self, search_text):
        if not search_text:
            for node in self.nodes:
                node.rect_item.setSelected(False)
                node.rect_item.setZValue(0)
            return

        for node in self.nodes:
            if search_text.lower() in node.text.lower():
                node.rect_item.setSelected(True)
                node.rect_item.setZValue(1)
                self._ensure_parents_visible(node)
            else:
                node.rect_item.setSelected(False)
                node.rect_item.setZValue(0)

    def _ensure_parents_visible(self, node):
        if node.parent:
            if node.parent.rect_item.collapsed:
                node.parent.rect_item.toggle_collapse()
            self._ensure_parents_visible(node.parent)

class MindMapView(QGraphicsView):
    """Custom view for displaying the mind map scene."""
    def __init__(self):
        super().__init__()
        self.setRenderHint(QPainter.Antialiasing)
        self.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAsNeeded)
        self.setScene(MindMapScene())
        self.setDragMode(QGraphicsView.ScrollHandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        
    def wheelEvent(self, event):
        if event.modifiers() & Qt.ControlModifier:
            factor = 1.1 if event.angleDelta().y() > 0 else 0.9
            self.scale(factor, factor)
        else:
            super().wheelEvent(event)

    def calculate_node_position(self, level, level_index):
        x = level * Node.HORIZONTAL_SPACING
        total_nodes = self.scene().level_counts.get(level, 1)
        y = (level_index - (total_nodes - 1) / 2) * Node.VERTICAL_SPACING
        return x, y

    def parse_and_render_markdown(self, text):
        self.scene().clear_nodes()
        self.parse_markdown_headings(text)
        
    def parse_markdown_headings(self, text):
        self.scene().level_counts = {}
        lines = [line.strip() for line in text.strip().split('\n') if line.strip()]
        
        for line in lines:
            if not line.startswith('#'):
                continue
            level = line.count('#', 0, line.find(' ')) - 1
            self.scene().level_counts[level] = self.scene().level_counts.get(level, 0) + 1

        current_levels = {}
        level_indices = {}
        
        for line in lines:
            if not line.startswith('#'):
                continue
                
            level = line.count('#', 0, line.find(' ')) - 1
            node_text = line.lstrip('# ').strip()
            
            if not node_text:
                continue
            
            level_indices[level] = level_indices.get(level, -1) + 1
                
            x, y = self.calculate_node_position(level, level_indices[level])
            
            colors = ["#3498db", "#e74c3c", "#2ecc71", "#f1c40f", "#9b59b6"]
            node = Node(node_text, x, y, colors[level % len(colors)])
            
            if level == 0:
                self.scene().add_node(node)
            else:
                parent = current_levels.get(level - 1)
                if parent:
                    self.scene().add_node(node, parent)
                    
            current_levels[level] = node

class EditorPanel(QFrame):
    """Panel for editing markdown text, with real-time updates via debounce timer."""
    renderRequested = Signal()

    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        
        toolbar = QToolBar()
        layout.addWidget(toolbar)
        
        self.new_action = QAction("New", self); self.new_action.setShortcut(QKeySequence.New)
        self.open_action = QAction("Open", self); self.open_action.setShortcut(QKeySequence.Open)
        self.save_action = QAction("Save", self); self.save_action.setShortcut(QKeySequence.Save)
        self.fit_view_action = QAction("Fit View", self); self.fit_view_action.setShortcut("Home")
        self.zoom_selection_action = QAction("Zoom to Selection", self); self.zoom_selection_action.setShortcut("F")
        self.fit_view_action.setToolTip("Fit the entire mind map in the view (Home)")
        self.zoom_selection_action.setToolTip("Zoom to the selected node (F)")

        toolbar.addAction(self.new_action)
        toolbar.addAction(self.open_action)
        toolbar.addAction(self.save_action)
        toolbar.addSeparator()
        toolbar.addAction(self.fit_view_action)
        toolbar.addAction(self.zoom_selection_action)
        
        search_layout = QHBoxLayout()
        search_label = QLabel("Search:")
        self.search_box = QLineEdit(); self.search_box.setPlaceholderText("Search nodes...")
        self.search_box.textChanged.connect(self.search_nodes)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_box)
        layout.addLayout(search_layout)

        title = QLabel("Markdown Editor")
        title.setFont(QFont("Segoe UI", 12, QFont.Bold))
        layout.addWidget(title)
        
        self.text_edit = QTextEdit()
        self.text_edit.setFont(QFont("Consolas", 11))
        self.text_edit.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Expanding)
        layout.addWidget(self.text_edit)
        
        button_grid = QGridLayout()
        self.render_button = QPushButton("Render"); self.render_button.setToolTip("Render mind map (Ctrl+R)")
        self.enhance_button = QPushButton("Enhance with AI"); self.enhance_button.setToolTip("Use AI to structure text (Ctrl+E)")
        self.export_button = QPushButton("Export"); self.export_button.setToolTip("Export as PNG/SVG")

        button_grid.addWidget(self.render_button, 0, 0)
        button_grid.addWidget(self.enhance_button, 0, 1)
        button_grid.addWidget(self.export_button, 1, 0, 1, 2)
        
        layout.addLayout(button_grid)
        
        self.breadcrumb_label = QLabel("No node selected")
        self.breadcrumb_label.setObjectName("BreadcrumbLabel")
        layout.addWidget(self.breadcrumb_label)

        self.render_debounce_timer = QTimer(self)
        self.render_debounce_timer.setSingleShot(True)
        self.render_debounce_timer.setInterval(750)
        self.render_debounce_timer.timeout.connect(self.request_render)

        self.text_edit.textChanged.connect(self.on_text_changed)
        self.mind_map_view = None

    def on_text_changed(self): self.render_debounce_timer.start()
    def request_render(self): self.renderRequested.emit()
    def search_nodes(self, text):
        if self.mind_map_view: self.mind_map_view.scene().search_nodes(text)

class TitleBar(QWidget):
    """custom title bar with standard icons and behavior."""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedHeight(30)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(8, 0, 0, 0)
        layout.setSpacing(0)

        self.title = QLabel("Mind Map Editor")
        self.title.setStyleSheet("color: #d4d4d4; font-size: 12px;")
        
        layout.addWidget(self.title)
        layout.addStretch()

        self.min_btn = QPushButton()
        self.min_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMinButton))
        self.min_btn.clicked.connect(self.window().showMinimized)

        self.max_btn = QPushButton()
        self.max_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarMaxButton))
        self.max_btn.clicked.connect(self.toggle_max)

        self.close_btn = QPushButton()
        self.close_btn.setIcon(self.style().standardIcon(QStyle.StandardPixmap.SP_TitleBarCloseButton))
        self.close_btn.clicked.connect(self.window().close)

        buttons = [self.min_btn, self.max_btn, self.close_btn]
        for btn in buttons:
            btn.setFixedSize(45, 30)
            btn.setIconSize(PySide6.QtCore.QSize(16, 16)) 
            btn.setStyleSheet("""
                QPushButton {
                    background-color: transparent;
                    border: none;
                    padding: 0px;
                }
                QPushButton:hover {
                    background-color: #404040;
                }
                QPushButton:pressed {
                    background-color: #333333;
                }
            """)
            layout.addWidget(btn)

        self.close_btn.setStyleSheet("""
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 0px;
            }
            QPushButton:hover {
                background-color: #e81123;
            }
            QPushButton:pressed {
                background-color: #cc0f1f;
            }
        """)

        self.setStyleSheet("background-color: #252526;")
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
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setGeometry(100, 100, 1200, 800)
        
        # This creates a thin 1px border around the entire application.
        self.setStyleSheet("background-color: #3f3f3f;")

        # Use QGridLayout to place the resize grip in the corner.
        main_layout = QGridLayout(self)
        main_layout.setContentsMargins(1, 1, 1, 1) # This margin works with the background color to create the border
        main_layout.setSpacing(0)

        # The rest of the content is now added to the grid
        self.title_bar = TitleBar(self)
        
        splitter = QSplitter(Qt.Horizontal)
        
        self.editor_panel = EditorPanel()
        self.editor_panel.setMinimumWidth(350)
        
        self.mind_map_view = MindMapView()
        
        splitter.addWidget(self.editor_panel)
        splitter.addWidget(self.mind_map_view)
        
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setSizes([400, 800])
        
        # Add widgets to the grid layout
        main_layout.addWidget(self.title_bar, 0, 0)
        main_layout.addWidget(splitter, 1, 0)

        # Make the main content area (row 1) stretchable
        main_layout.setRowStretch(1, 1)
        
        # Use a container widget for styling, so the main window's background (the border) is not affected
        container_widget = QWidget()
        container_widget.setLayout(main_layout)
        container_widget.setStyleSheet(StyleSheet.DARK_THEME)

        # Add the QSizeGrip for resizing
        size_grip = QSizeGrip(container_widget)
        main_layout.addWidget(size_grip, 1, 0, Qt.AlignBottom | Qt.AlignRight)
        
        # Set the main layout for the window
        root_layout = QVBoxLayout(self)
        root_layout.setContentsMargins(0,0,0,0)
        root_layout.addWidget(container_widget)

        self.setWindowTitle("Mind Map Editor")
        self.editor_panel.mind_map_view = self.mind_map_view
        
        self.current_file = None
        self.ai_worker = None
        self.setup_connections()
        self.load_example_content()

    def changeEvent(self, event):
        """Handle window state changes to update the maximize button icon."""
        if event.type() == QEvent.Type.WindowStateChange:
            self.title_bar.update_maximize_button_icon()
        
    def setWindowTitle(self, title):
        super().setWindowTitle(title)
        self.title_bar.title.setText(title)

    def setup_connections(self):
        """Sets up signal-slot connections for actions and buttons."""
        self.editor_panel.render_button.clicked.connect(self.render_markdown)
        self.editor_panel.export_button.clicked.connect(self.export_mind_map)
        self.editor_panel.new_action.triggered.connect(self.new_file)
        self.editor_panel.open_action.triggered.connect(self.open_file)
        self.editor_panel.save_action.triggered.connect(self.save_file)
        self.editor_panel.render_button.setShortcut("Ctrl+R")
        self.editor_panel.enhance_button.clicked.connect(self.enhance_with_ai)
        self.editor_panel.enhance_button.setShortcut("Ctrl+E")
        self.editor_panel.renderRequested.connect(self.render_markdown)
        self.mind_map_view.scene().nodeSelected.connect(self.handle_node_selection)
        self.editor_panel.fit_view_action.triggered.connect(self.fit_view)
        self.editor_panel.zoom_selection_action.triggered.connect(self.zoom_to_selection)

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
        self.editor_panel.enhance_button.setEnabled(False)
        self.editor_panel.render_button.setEnabled(False)
        self.editor_panel.enhance_button.setText("Processing...")
        self.ai_worker = AIWorker(raw_text)
        self.ai_worker.finished.connect(self.handle_ai_result)
        self.ai_worker.error.connect(self.handle_ai_error)
        self.ai_worker.start()

    def handle_ai_result(self, markdown_text):
        self.editor_panel.text_edit.textChanged.disconnect(self.editor_panel.on_text_changed)
        self.editor_panel.text_edit.setText(markdown_text)
        self.editor_panel.text_edit.textChanged.connect(self.editor_panel.on_text_changed)
        self.render_markdown()
        self.reset_ai_button_state()
        QMessageBox.information(self, "Success", "AI enhancement complete.")

    def handle_ai_error(self, error_message):
        QMessageBox.critical(self, "AI Error", error_message)
        self.reset_ai_button_state()

    def reset_ai_button_state(self):
        self.editor_panel.enhance_button.setEnabled(True)
        self.editor_panel.render_button.setEnabled(True)
        self.editor_panel.enhance_button.setText("Enhance with AI")

    def load_example_content(self):
        example_text = """# Mind Map Tutorial And A Really Long Title To Test Wrapping
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
        menu = QMenu(self)
        export_png = menu.addAction("Export as PNG")
        export_svg = menu.addAction("Export as SVG")
        action = menu.exec(self.editor_panel.export_button.mapToGlobal(self.editor_panel.export_button.rect().bottomLeft()))
        if action == export_png: self.export_as_png()
        elif action == export_svg: self.export_as_svg()

    def export_as_png(self):
        file_name, _ = QFileDialog.getSaveFileName(self, "Export as PNG", "", "PNG Files (*.png)")
        if file_name:
            scene = self.mind_map_view.scene()
            scene_rect = scene.itemsBoundingRect()
            image = QImage(int(scene_rect.width()), int(scene_rect.height()), QImage.Format_ARGB32)
            image.fill(Qt.transparent)
            painter = QPainter(image)
            painter.setRenderHint(QPainter.Antialiasing)
            scene.render(painter, QRectF(image.rect()), scene_rect)
            painter.end()
            image.save(file_name)
            QMessageBox.information(self, "Export Successful", f"Mind map exported to {file_name}")

    def export_as_svg(self):
        QMessageBox.warning(self, "Not Implemented", "SVG export is not yet fully implemented.")

    def handle_node_selection(self, node):
        if node:
            path = []; curr = node
            while curr: path.append(curr.text); curr = curr.parent
            self.editor_panel.breadcrumb_label.setText(" > ".join(reversed(path)))
        else:
            self.editor_panel.breadcrumb_label.setText("No node selected")
            return

        text = self.editor_panel.text_edit.toPlainText(); lines = text.split('\n')
        for i, line in enumerate(lines):
            if line.lstrip('# ').strip() == node.text:
                cursor = self.editor_panel.text_edit.textCursor()
                cursor.movePosition(QTextCursor.MoveOperation.Start)
                cursor.movePosition(QTextCursor.MoveOperation.Down, QTextCursor.MoveMode.MoveAnchor, i)
                cursor.movePosition(QTextCursor.MoveOperation.EndOfLine, QTextCursor.MoveMode.KeepAnchor)
                self.editor_panel.text_edit.setTextCursor(cursor)
                break

    def render_markdown(self):
        markdown_text = self.editor_panel.text_edit.toPlainText()
        self.mind_map_view.parse_and_render_markdown(markdown_text)
        self.fit_view()

def main():
    """Entry point for the application."""
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
