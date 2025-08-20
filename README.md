Of course. Here is a more professional version of the README without emojis and with a more direct tone.

---

# Tree-Graph-MindMap: AI-Powered Mind Map Generator

This application transforms raw, unstructured text into an interactive mind map. It uses local Large Language Models (LLMs) via [Ollama](https://ollama.com/) to intelligently structure information, which is then visualized from a simple Markdown file.

![Untitled video - Made with Clipchamp (1)](https://github.com/user-attachments/assets/17718da0-b5ef-4b2c-a0f6-99d7eb9b5cff)


## Features

-   **AI-Powered Structuring**: Uses a local LLM via Ollama to transform unstructured text into a hierarchical Markdown document suitable for visualization.
-   **Markdown-Driven**: The mind map is generated directly from a Markdown file. The visualization updates in near real-time as you edit the text.
-   **Interactive Canvas**:
    -   **Pan and Zoom**: Navigate the map by dragging the canvas and using Ctrl+Scroll to zoom.
    -   **Movable Nodes**: Freely reposition nodes; connectors will update automatically.
    -   **Collapsible Branches**: Collapse and expand branches of the mind map to focus on specific areas.
    -   **Node Coloring**: Customize node colors via a color picker on double-click.
-   **Editor-Canvas Synchronization**: Selecting a node on the canvas highlights the corresponding line in the Markdown editor.
-   **Node Search**: A search bar allows for quick filtering and finding of nodes.
-   **PNG Export**: Export the entire mind map as a high-resolution, transparent PNG image.
-   **Modern UI**: A custom, frameless dark-themed interface built with PySide6.

## How It Works

The application operates on three core principles:

1.  **Markdown as the Data Source**: The mind map's structure is defined by Markdown headings. A level 1 heading (`# Title`) is the root node, a level 2 heading (`## Sub-Topic`) is a child of the root, and deeper headings create subsequent branches.
2.  **AI for Structuring**: The "Enhance with AI" feature sends the input text to a locally running Ollama model. A system prompt directs the model to analyze the text, identify its underlying structure, and return a well-formed Markdown document.
3.  **Dynamic Rendering**: The application parses the Markdown in the editor and renders it as an interactive graph. A debounce timer automatically updates the visualization as the user types, ensuring a responsive experience.

## Prerequisites

To run this application, you will need:

1.  **Python 3.8+**
2.  The `PySide6` and `ollama` Python libraries.
3.  **[Ollama](https://ollama.com/)**: The Ollama service must be installed and running locally.
4.  **An Ollama Model**: At least one model must be pulled for the AI features to work. The application defaults to `phi4:14b`, but this can be changed in the source code.

    ```bash
    # Pull the recommended model
    ollama pull phi4:14b
    ```

## Installation and Usage

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dovvnloading/Tree-Graph-MindMap.git
    cd Tree-Graph-MindMap
    ```

2.  **Install dependencies:**
    ```bash
    pip install PySide6 ollama
    ```

3.  **Start the Ollama service.** This can be done by running `ollama serve` in a terminal or by launching the Ollama desktop application.

4.  **Run the application:**
    ```bash
    python main.py
    ```
    *(Note: You may need to use `python3` depending on your system's configuration.)*

## Using the AI Enhancement

The AI enhancement feature restructures raw text into a hierarchical format.

1.  Paste unstructured text into the Markdown editor panel. For example:

    > Our company project, Phoenix, is running behind. The UI/UX team is blocked because the backend APIs are not ready. Specifically, the authentication endpoint is down, and the user profile service is returning 500 errors. On the frontend side, the component library needs to be updated to version 3.1, which is a breaking change.

2.  Click the **"Enhance with AI"** button or press `Ctrl+E`.

3.  The AI will process the input and replace it with a structured Markdown document, which is then rendered as a mind map.

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

## Keyboard Shortcuts

| Shortcut      | Action                               |
| ------------- | ------------------------------------ |
| `Ctrl + R`    | Manually render the mind map.        |
| `Ctrl + E`    | Enhance the current text with AI.    |
| `Ctrl + S`    | Save the current Markdown file.      |
| `Ctrl + O`    | Open a Markdown file.                |
| `Ctrl + N`    | Create a new, empty file.            |
| `Home`        | Fit the entire mind map in the view. |
| `F`           | Zoom to the currently selected node. |

## Contributing

Contributions, issues, and feature requests are welcome. Please refer to the [issues page](https://github.com/dovvnloading/Tree-Graph-MindMap/issues) for an overview of current tasks and bugs.

## License

This project is open-source. Please refer to the LICENSE file for more details.
