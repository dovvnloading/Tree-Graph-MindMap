
# Tree-Graph-MindMap: AI-Powered Mind Map Generator

Instantly turn your raw notes, brainstorming sessions, or any unstructured text into a beautiful, interactive mind map. This application leverages the power of local Large Language Models (LLMs) via [Ollama](https://ollama.com/) to intelligently structure your information, which is then visualized from a simple Markdown file.

![Untitled video - Made with Clipchamp (1)](https://github.com/user-attachments/assets/495280f0-3c15-476b-8912-8187dcaba1e2)


## ✨ Features

-   **🤖 AI-Powered Structuring**: Paste any text, click "Enhance with AI", and watch as a local LLM transforms it into a perfectly hierarchical Markdown structure, ready for visualization.
-   **✍️ Markdown-Driven**: The mind map is a direct representation of a simple Markdown file. Edit the text using standard heading syntax (`#`, `##`, etc.), and the map updates in real-time.
-   **🎨 Interactive Canvas**:
    -   **Pan & Zoom**: Navigate your mind map with ease (Drag to pan, Ctrl+Scroll to zoom).
    -   **Movable Nodes**: Drag and drop nodes to customize the layout. Connections automatically adjust.
    -   **Collapsible Branches**: Click the `+/-` icon on a node to hide or show its children, allowing you to focus on specific parts of the map.
    -   **Node Coloring**: Double-click any node to open a color picker and change its color.
-   **↔️ Editor-Canvas Sync**: Click a node in the mind map, and the corresponding line is instantly highlighted in the Markdown editor.
-   **🔍 Quick Search**: Find any node in your map with the built-in search bar.
-   **🖼️ Export to PNG**: Save your finished mind map as a high-resolution, transparent PNG image.
-   ** sleek Dark UI**: A modern, dark-themed interface built with PySide6, featuring a custom frameless window.

## ⚙️ How It Works

The application is built around a simple but powerful concept:

1.  **Markdown as the Source of Truth**: The structure of your mind map is defined by Markdown headings. A level 1 heading (`# Title`) becomes the root node, a level 2 heading (`## Sub-Topic`) becomes a child of the root, and so on.
2.  **AI for Intelligence**: The "Enhance with AI" feature sends your raw text to a locally running Ollama model. A specialized system prompt instructs the model to act as an information architect, identifying themes and hierarchies and outputting a clean Markdown structure.
3.  **Real-time Visualization**: The application parses the Markdown text and dynamically renders it as a graph of connected nodes on the canvas. A debounce timer ensures the map updates automatically as you type without overwhelming the system.

##  prerequisites

Before you begin, ensure you have the following installed and running:

1.  **Python 3.8+**
2.  **PySide6** and **Ollama** Python libraries.
3.  **[Ollama](https://ollama.com/)**: You must have the Ollama service installed and **running on your machine**. This application communicates with your local Ollama instance.
4.  **An Ollama Model**: You need to have a model pulled to use the AI features. The application defaults to `phi3`, but you can edit the source code to use any model you prefer.

    ```bash
    # Pull the recommended model
    ollama pull phi4
    ```

## 🚀 Installation & Usage

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dovvnloading/Tree-Graph-MindMap.git
    cd Tree-Graph-MindMap
    ```

2.  **Install the required Python packages:**
    ```bash
    pip install PySide6 ollama
    ```

3.  **Ensure the Ollama service is running.** You can typically start it by running `ollama serve` in a separate terminal or by launching the Ollama desktop application.

4.  **Run the application:**
    ```bash
    python main.py
    ```
    *(Note: You may need to use `python3` depending on your system's configuration.)*

## 🧠 Using the AI Enhancement

This is the standout feature of the application.

1.  Paste any block of unstructured text into the Markdown editor. For example:

    > *Our company project, Phoenix, is running behind. The UI/UX team is blocked because the backend APIs are not ready. Specifically, the authentication endpoint is down, and the user profile service is returning 500 errors. On the frontend side, the component library needs to be updated to version 3.1, which is a breaking change.*

2.  Click the **"Enhance with AI"** button (or press `Ctrl+E`).

3.  The application will process the text and replace it with a structured Markdown document. The mind map will automatically render this new structure.

    ```markdown
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
    ```

## ⌨️ Keyboard Shortcuts

| Shortcut      | Action                               |
| ------------- | ------------------------------------ |
| `Ctrl + R`    | Manually render the mind map.        |
| `Ctrl + E`    | Enhance the current text with AI.    |
| `Ctrl + S`    | Save the current Markdown file.      |
| `Ctrl + O`    | Open a Markdown file.                |
| `Ctrl + N`    | Create a new, empty file.            |
| `Home`        | Fit the entire mind map in the view. |
| `F`           | Zoom to the currently selected node. |

## 🤝 Contributing

Contributions, issues, and feature requests are welcome! Feel free to check the [issues page](https://github.com/dovvnloading/Tree-Graph-MindMap/issues).

## 📄 License

This project is open-source. Please refer to the LICENSE file for more details. *(Assuming a license will be added)*.****
