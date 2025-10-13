import PySide6.QtCore

from PySide6.QtGui import QPainterPath, QPainter, QPen, QColor, QBrush, QFont
from PySide6.QtWidgets import (QGraphicsScene, QGraphicsView, QGraphicsItem, 
                               QColorDialog, QGraphicsPathItem)
from PySide6.QtCore import Qt, QRectF, QPointF, Signal

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
        if change == QGraphicsItem.ItemPositionChange and self.scene():
            new_pos = value
            scene = self.scene()

            if scene.snap_to_grid:
                grid_size = scene.grid_size
                snapped_x = round(value.x() / grid_size) * grid_size
                snapped_y = round(value.y() / grid_size) * grid_size
                snapped_pos = QPointF(snapped_x, snapped_y)

                # Check for collisions at the snapped position.
                check_rect = self.rect.translated(snapped_pos)
                colliding_items = scene.items(check_rect)
                
                collision_found = False
                for item in colliding_items:
                    if isinstance(item, RoundedRectItem) and item is not self:
                        collision_found = True
                        break
                
                if not collision_found:
                    new_pos = snapped_pos
            
            self.node.x = new_pos.x()
            self.node.y = new_pos.y()
            
            if self.node.incoming_connection:
                self.node.incoming_connection.update_path()
            for conn in self.node.outgoing_connections:
                conn.update_path()
            
            self.scene().update()
            
            return new_pos

        return super().itemChange(change, value)

class Node:
    """Represents a node in the mind map hierarchy."""
    WIDTH = 200
    HEIGHT = 50
    HORIZONTAL_SPACING = 300
    VERTICAL_SPACING = 100
    
    def __init__(self, text, x, y, line_number, color="#3498db"):
        self.text = text
        self.x = x
        self.y = y
        self.width = self.WIDTH
        self.height = self.HEIGHT
        self.color = color
        self.line_number = line_number
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
        self.setBackgroundBrush(QColor("#2a2a2a"))
        self.selected_node = None
        self.node_text_color = QColor("#ffffff")
        self.grid_size = 20
        self.snap_to_grid = False
        
    def set_snap_to_grid(self, enabled: bool):
        self.snap_to_grid = enabled
        
    def set_theme(self, is_dark_theme: bool):
        self.node_text_color = QColor("#ffffff") if is_dark_theme else QColor("#1e1e1e")
        for item in self.items():
            if isinstance(item, PySide6.QtWidgets.QGraphicsTextItem):
                item.setDefaultTextColor(self.node_text_color)
        self.update()
        
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
        node.text_item.setDefaultTextColor(self.node_text_color)
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
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.is_dark_theme = True
        self.is_panning = False
        self.last_pan_point = QPointF()
        
    def set_snap_to_grid(self, enabled: bool):
        self.scene().set_snap_to_grid(enabled)

    def set_theme(self, is_dark_theme: bool):
        self.is_dark_theme = is_dark_theme
        self.scene().set_theme(is_dark_theme)

    def drawBackground(self, painter, rect):
        super().drawBackground(painter, rect)
        grid_size = self.scene().grid_size
        
        left = int(rect.left()) - (int(rect.left()) % grid_size)
        top = int(rect.top()) - (int(rect.top()) % grid_size)
        
        grid_color = QColor(60, 60, 60) if self.is_dark_theme else QColor(220, 220, 220)
        pen = QPen(grid_color, 1, Qt.DotLine)
        painter.setPen(pen)

        for x in range(left, int(rect.right()), grid_size):
            painter.drawLine(x, int(rect.top()), x, int(rect.bottom()))
        for y in range(top, int(rect.bottom()), grid_size):
            painter.drawLine(int(rect.left()), y, int(rect.right()), y)
            
    def mousePressEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.is_panning = True
            self.last_pan_point = event.pos()
            self.setCursor(Qt.ClosedHandCursor)
            event.accept()
        else:
            super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.is_panning:
            delta = event.pos() - self.last_pan_point
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - delta.x())
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - delta.y())
            self.last_pan_point = event.pos()
            event.accept()
        else:
            super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MiddleButton:
            self.is_panning = False
            self.setCursor(Qt.ArrowCursor)
            event.accept()
        else:
            super().mouseReleaseEvent(event)

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
        lines = text.split('\n')

        # First pass: count nodes at each level for layout calculation
        for line in lines:
            stripped_line = line.strip()
            if stripped_line and stripped_line.startswith('#'):
                level = stripped_line.count('#', 0, stripped_line.find(' ')) - 1
                self.scene().level_counts[level] = self.scene().level_counts.get(level, 0) + 1

        current_levels = {}
        level_indices = {}
        
        # Second pass: create and position nodes
        for line_idx, line in enumerate(lines):
            stripped_line = line.strip()
            if not stripped_line or not stripped_line.startswith('#'):
                continue
                
            level = stripped_line.count('#', 0, stripped_line.find(' ')) - 1
            node_text = stripped_line.lstrip('# ').strip()
            
            if not node_text:
                continue
            
            level_indices[level] = level_indices.get(level, -1) + 1
                
            x, y = self.calculate_node_position(level, level_indices[level])
            
            colors = ["#3498db", "#e74c3c", "#2ecc71", "#f1c40f", "#9b59b6"]
            node = Node(node_text, x, y, line_idx, colors[level % len(colors)])
            
            if level == 0:
                self.scene().add_node(node)
            else:
                parent = current_levels.get(level - 1)
                if parent:
                    self.scene().add_node(node, parent)
                    
            current_levels[level] = node