import ollama
from PySide6.QtCore import QThread, Signal, QByteArray, Qt
from PySide6.QtGui import QIcon, QColor, QPixmap, QPainter
from PySide6.QtSvg import QSvgRenderer

# --- Icon Generation System ---

class IconFactory:
    """Creates theme-aware QIcons from SVG data."""
    _SVG_DATA = {
        "new": '<path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"></path><polyline points="14 2 14 8 20 8"></polyline><line x1="12" y1="18" x2="12" y2="12"></line><line x1="9" y1="15" x2="15" y2="15"></line>',
        "open": '<path d="M22 19a2 2 0 0 1-2 2H4a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h5l2 3h9a2 2 0 0 1 2 2z"></path>',
        "save": '<path d="M19 21H5a2 2 0 0 1-2-2V5a2 2 0 0 1 2-2h11l5 5v11a2 2 0 0 1-2 2z"></path><polyline points="17 21 17 13 7 13 7 21"></polyline><polyline points="7 3 7 8 15 8"></polyline>',
        "render": '<polyline points="23 4 23 10 17 10"></polyline><polyline points="1 20 1 14 7 14"></polyline><path d="M3.51 9a9 9 0 0 1 14.85-3.36L23 10M1 14l4.64 4.36A9 9 0 0 0 20.49 15"></path>',
        "enhance": '<rect x="4" y="4" width="16" height="16" rx="2" ry="2"></rect><rect x="9" y="9" width="6" height="6"></rect><line x1="9" y1="1" x2="9" y2="4"></line><line x1="15" y1="1" x2="15" y2="4"></line><line x1="9" y1="20" x2="9" y2="23"></line><line x1="15" y1="20" x2="15" y2="23"></line><line x1="20" y1="9" x2="23" y2="9"></line><line x1="20" y1="14" x2="23" y2="14"></line><line x1="1" y1="9" x2="4" y2="9"></line><line x1="1" y1="14" x2="4" y2="14"></line>',
        "export": '<path d="M18 13v6a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2V8a2 2 0 0 1 2-2h6"></path><polyline points="15 3 21 3 21 9"></polyline><line x1="10" y1="14" x2="21" y2="3"></line>'
    }

    @staticmethod
    def create_icon(name: str, color: QColor) -> QIcon:
        """
        Creates a QIcon from stored SVG data, tinted with the specified color.
        """
        svg_path_data = IconFactory._SVG_DATA.get(name)
        if not svg_path_data:
            return QIcon()

        full_svg = f'<svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round">{svg_path_data}</svg>'
        
        renderer = QSvgRenderer(QByteArray(full_svg.encode('utf-8')))
        
        pixmap = QPixmap(renderer.defaultSize())
        pixmap.fill(Qt.transparent)
        
        painter = QPainter(pixmap)
        renderer.render(painter)
        
        painter.setCompositionMode(QPainter.CompositionMode_SourceIn)
        painter.fillRect(pixmap.rect(), color)
        painter.end()
        
        return QIcon(pixmap)

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

---

Do not make the graphs too long! Unless explicitly requested otherwise.
"""

class AIWorker(QThread):
    """Worker thread to process text with Ollama without freezing the UI."""
    finished = Signal(str)
    error = Signal(str)

    def __init__(self, text_to_process, model='qwen3:8b'):
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
    """Defines stylesheets for the application, supporting light and dark themes."""
    DARK_THEME = """
        /* General */
        #MainWindowContainer, QMenu, QColorDialog {
            background-color: #1e1e1e;
            color: #d4d4d4;
        }

        /* Title Bar */
        #TitleBar { background-color: #252526; }
        #TitleBarLabel { color: #d4d4d4; font-size: 12px; border: none; background: transparent; }
        #TitleBar QPushButton { background-color: transparent; border: none; padding: 0px; }
        #TitleBar QPushButton:hover { background-color: #404040; }
        #TitleBar QPushButton:pressed { background-color: #333333; }
        #TitleBar #CloseButton:hover { background-color: #e81123; }
        #TitleBar #CloseButton:pressed { background-color: #cc0f1f; }

        /* Left Panel */
        #EditorPanel { background-color: #1e1e1e; border: none; }
        #StatusBar {
            background-color: #252526;
            border-top: 1px solid #3f3f3f;
        }
        #StatusBar #BreadcrumbLabel {
            color: #9e9e9e;
            font-weight: normal;
            font-size: 9pt;
            padding: 6px 10px;
            background-color: transparent;
            border: none;
        }

        /* Widgets */
        QTextEdit {
            background-color: #252526;
            color: #d4d4d4;
            border: none;
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
        QPushButton:hover { background-color: #1177bb; }
        QPushButton:pressed { background-color: #0d5485; }
        QPushButton:disabled { background-color: #2d3e49; color: #7b8a93; }

        QGraphicsView {
            background-color: #2a2a2a;
            border: none;
            border-radius: 4px;
        }
        QLabel { color: #d4d4d4; font-weight: normal; border: none; }
        QSplitter::handle {
            background-color: #3f3f3f;
            border: none;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNCIgaGVpZ2h0PSIxNiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIyIiBjeT0iMiIgcj0iMSIgZmlsbD0iIzY2NjY2NiIvPjxjaXJjbGUgY3g9IjIiIGN5PSI4IiByPSIxIiBmaWxsPSIjNjY2NjY2Ii8+PGNpcmNsZSBjeD0iMiIgY3k9IjE0IiByPSIxIiBmaWxsPSIjNjY2NjY2Ii8+PC9zdmc+);
            background-repeat: no-repeat;
            background-position: center center;
        }
        QSplitter::handle:hover { background-color: #5a5a5a; }

        /* Toolbar */
        #MainToolbar {
            background-color: #252526;
            border-bottom: 1px solid #3f3f3f;
            spacing: 4px;
            padding: 2px 8px;
        }
        #MainToolbar QToolButton {
            color: #d4d4d4;
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 4px;
            padding: 6px 8px;
        }
        #MainToolbar QToolButton:hover { background-color: #3e3e3e; }
        #MainToolbar QToolButton:pressed { background-color: #333333; }
        #MainToolbar QToolButton:on { background-color: #0e639c; } /* Style for when menu is open */
        
        #MainToolbar QLineEdit {
            background-color: #313131;
            color: #d4d4d4;
            border: 1px solid #3f3f3f;
            border-radius: 4px;
            padding: 4px 8px;
        }
        #MainToolbar QLineEdit:focus { border-color: #0e639c; }

        /* Menu */
        QMenu { background-color: #252526; border: 1px solid #555555; }
        QMenu::item { padding: 6px 24px; color: #d4d4d4; }
        QMenu::item:selected { background-color: #0e639c; }
        
        /* ScrollBar */
        QScrollBar:vertical {
            border: none;
            background: #252526;
            width: 12px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: #4f4f4f;
            min-height: 20px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical:hover { background: #5a5a5a; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; background: none; }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

        QScrollBar:horizontal {
            border: none;
            background: #252526;
            height: 12px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:horizontal {
            background: #4f4f4f;
            min-width: 20px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal:hover { background: #5a5a5a; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; background: none; }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }
    """
    
    LIGHT_THEME = """
        /* General */
        #MainWindowContainer, QMenu, QColorDialog {
            background-color: #f0f0f0;
            color: #1e1e1e;
        }

        /* Title Bar */
        #TitleBar { background-color: #e1e1e1; }
        #TitleBarLabel { color: #1e1e1e; font-size: 12px; border: none; background: transparent; }
        #TitleBar QPushButton { background-color: transparent; border: none; padding: 0px; }
        #TitleBar QPushButton:hover { background-color: #d5d5d5; }
        #TitleBar QPushButton:pressed { background-color: #cccccc; }
        #TitleBar #CloseButton:hover { background-color: #e81123; }
        #TitleBar #CloseButton:pressed { background-color: #cc0f1f; }

        /* Left Panel */
        #EditorPanel { background-color: #f0f0f0; border: none; }
        #StatusBar {
            background-color: #e1e1e1;
            border-top: 1px solid #cccccc;
        }
        #StatusBar #BreadcrumbLabel {
            color: #555555;
            font-weight: normal;
            font-size: 9pt;
            padding: 6px 10px;
            background-color: transparent;
            border: none;
        }

        /* Widgets */
        QTextEdit {
            background-color: #ffffff;
            color: #1e1e1e;
            border: none;
            padding: 8px;
            selection-background-color: #a8c8e8;
            font-family: 'Consolas', monospace;
        }
        QPushButton {
            background-color: #007acc;
            color: white;
            border: none;
            padding: 8px 16px;
            border-radius: 4px;
            font-weight: bold;
            min-height: 30px; 
        }
        QPushButton:hover { background-color: #008ae6; }
        QPushButton:pressed { background-color: #006bb3; }
        QPushButton:disabled { background-color: #d3d3d3; color: #888888; }

        QGraphicsView {
            background-color: #ffffff;
            border: none;
            border-radius: 4px;
        }
        QLabel { color: #1e1e1e; font-weight: normal; border: none; }
        QSplitter::handle {
            background-color: #cccccc;
            border: none;
            image: url(data:image/svg+xml;base64,PHN2ZyB3aWR0aD0iNCIgaGVpZ2h0PSIxNiIgeG1sbnM9Imh0dHA6Ly93d3cudzMub3JnLzIwMDAvc3ZnIj48Y2lyY2xlIGN4PSIyIiBjeT0iMiIgcj0iMSIgZmlsbD0iIzg4ODg4OCIvPjxjaXJjbGUgY3g9IjIiIGN5PSI4IiByPSIxIiBmaWxsPSIjODg4ODg4Ii8+PGNpcmNsZSBjeD0iMiIgY3k9IjE0IiByPSIxIiBmaWxsPSIjODg4ODg4Ii8+PC9zdmc+);
            background-repeat: no-repeat;
            background-position: center center;
        }
        QSplitter::handle:hover { background-color: #bbbbbb; }

        /* Toolbar */
        #MainToolbar {
            background-color: #e1e1e1;
            border-bottom: 1px solid #cccccc;
            spacing: 4px;
            padding: 2px 8px;
        }
        #MainToolbar QToolButton {
            color: #1e1e1e;
            background-color: transparent;
            border: 1px solid transparent;
            border-radius: 4px;
            padding: 6px 8px;
        }
        #MainToolbar QToolButton:hover { background-color: #dcdcdc; }
        #MainToolbar QToolButton:pressed { background-color: #cccccc; }
        #MainToolbar QToolButton:on { background-color: #007acc; color: white; }

        #MainToolbar QLineEdit {
            background-color: #ffffff;
            color: #1e1e1e;
            border: 1px solid #cccccc;
            border-radius: 4px;
            padding: 4px 8px;
        }
        #MainToolbar QLineEdit:focus { border-color: #007acc; }

        /* Menu */
        QMenu { background-color: #ffffff; border: 1px solid #cccccc; }
        QMenu::item { padding: 6px 24px; color: #1e1e1e; }
        QMenu::item:selected { background-color: #007acc; color: white; }
        
        /* ScrollBar */
        QScrollBar:vertical {
            border: none;
            background: #e1e1e1;
            width: 12px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:vertical {
            background: #b1b1b1;
            min-height: 20px;
            border-radius: 6px;
        }
        QScrollBar::handle:vertical:hover { background: #a1a1a1; }
        QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; background: none; }
        QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical { background: none; }

        QScrollBar:horizontal {
            border: none;
            background: #e1e1e1;
            height: 12px;
            margin: 0px 0px 0px 0px;
        }
        QScrollBar::handle:horizontal {
            background: #b1b1b1;
            min-width: 20px;
            border-radius: 6px;
        }
        QScrollBar::handle:horizontal:hover { background: #a1a1a1; }
        QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; background: none; }
        QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal { background: none; }
    """