<img width="883" height="412" alt="Mind MAp_Banner_001" src="https://github.com/user-attachments/assets/c30079c1-9c6f-4e6a-a2d3-05e005691062" />

# AI-Powered Mind Map Generator

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue?logo=python&logoColor=white" alt="Python 3.8+">
  <img src="https://img.shields.io/badge/Framework-PySide6-2492C1?logo=qt" alt="PySide6">
  <img src="https://img.shields.io/badge/AI-Ollama-black?logo=ollama" alt="Ollama">
  <img src="https://img.shields.io/badge/license-MIT-green" alt="License: MIT">
  <img src="https://img.shields.io/badge/PRs-welcome-brightgreen.svg" alt="PRs Welcome">
</p>

An intuitive desktop application that transforms raw, unstructured text into interactive mind maps. It leverages the power of local Large Language Models (LLMs) via **[Ollama](https://ollama.com/)** to intelligently structure information, which is then visualized from a simple Markdown file.

---

### Demonstration
![Untitled video - Made with Clipchamp (16)](https://github.com/user-attachments/assets/a7768c1b-62dd-4e24-8459-99bff6fb570e)



<p align="center">
  <img width="1600" height="900" alt="Screenshot 2025-10-13 103623" src="https://github.com/user-attachments/assets/94debfc5-c9d4-4843-aa65-595fae792c0b" />
<img width="1600" height="900" alt="Screenshot 2025-10-13 103616" src="https://github.com/user-attachments/assets/13363f90-9da2-4444-ac9d-936eec4d1aed" />

</p>

## Key Features

### AI-Powered Structuring
-   **Intelligent Text Analysis**: Uses a local LLM via Ollama to transform unstructured text into a hierarchical Markdown document suitable for visualization.
-   **One-Click Enhancement**: Structure meeting notes, brainstorms, or copied text into a clean mind map structure with a single click (`Ctrl+E`).

### Modern and Interactive Canvas
-   **Markdown-Driven**: The mind map is generated directly from Markdown. The visualization updates in near real-time as you edit.
-   **Comprehensive Navigation**: Pan the canvas with a middle-mouse drag and use `Ctrl+Scroll` to zoom.
-   **Dynamic Nodes**: Freely reposition nodes; connectors will fluidly update automatically. Collapse and expand branches to focus on specific areas.
-   **Node Customization**: Customize node colors via a color picker on double-click.
-   **Visual Aids**: Toggleable grid and snap-to-grid functionality for precise node alignment.

### Professional User Experience
-   **Dual Themes**: Switch between a sleek dark theme and a clean light theme. Icons and UI elements adapt for optimal visibility.
-   **Productivity Tools**: Quickly find nodes with the integrated search bar, and use keyboard shortcuts for all major actions.
-   **PNG Export**: Export the entire mind map as a high-resolution, transparent PNG image, perfectly cropped to fit the content.
-   **Modern UI**: A custom, frameless interface built with PySide6 for a native application experience.

## How It Works

The application operates on three core principles:

1.  **Markdown as the Data Source**: The mind map's structure is defined by Markdown headings. A level 1 heading (`# Title`) is the root node, a level 2 heading (`## Sub-Topic`) is a child of the root, and deeper headings create subsequent branches.
2.  **AI for Structuring**: The "AI Enhance" feature sends the input text to a locally running Ollama model. A system prompt directs the model to analyze the text, identify its underlying structure, and return a well-formed Markdown document.
3.  **Dynamic Rendering**: The application parses the Markdown in the editor and renders it as an interactive graph. A debounce timer automatically updates the visualization as the user types, ensuring a responsive experience without requiring manual refreshes.

## Getting Started

### Prerequisites

1.  **Python 3.8+**
2.  **[Ollama](https://ollama.com/)**: The Ollama service must be installed and running locally.
3.  **An Ollama Model**: At least one model must be downloaded for the AI features to work. The application defaults to a small, fast model, but this can be changed in the source code.

    ```bash
    # Pull the recommended model (fast and lightweight)
    ollama pull granite4:tiny-h
    ```

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/dovvnloading/Tree-Graph-MindMap.git
    cd Tree-Graph-MindMap
    ```

2.  **Install Python dependencies:**
    ```bash
    pip install PySide6 ollama
    ```

3.  **Start the Ollama service.** This is typically done by launching the Ollama desktop application or running `ollama serve` in a terminal.

4.  **Run the application:**
    ```bash
    python Mind_Map.py
    ```
    *(Note: You may need to use `python3` depending on your system's configuration.)*

## Core Usage

The AI enhancement feature is designed to bring structure to complex information.

1.  Paste any unstructured text into the Markdown editor panel. For example:

    > Our company project, Phoenix, is running behind. The UI/UX team is blocked because the backend APIs are not ready. Specifically, the authentication endpoint is down, and the user profile service is returning 500 errors. On the frontend side, the component library needs to be updated to version 3.1, which is a breaking change.

2.  Click the **"AI Enhance"** button in the toolbar or press `Ctrl+E`.

3.  The AI will process the input and replace it with a structured Markdown document, which is then instantly rendered as a mind map.

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

| Shortcut           | Action                               |
| ------------------ | ------------------------------------ |
| `Ctrl + R`         | Manually render the mind map.        |
| `Ctrl + E`         | Enhance the current text with AI.    |
| `Ctrl + Shift + E` | Export the mind map as a PNG image.  |
| `Ctrl + S`         | Save the current Markdown file.      |
| `Ctrl + O`         | Open a Markdown file.                |
| `Ctrl + N`         | Create a new, empty file.            |
| `Home`             | Fit the entire mind map in the view. |
| `F`                | Zoom to the currently selected node. |

## Configuration

The default AI model can be changed by editing the `AIWorker` class initialization in `app_utils.py`. Simply replace `'granite4:tiny-h'` with the name of any other model you have installed via Ollama.

## Contributing

Contributions, issues, and feature requests are welcome. Please refer to the [issues page](https://github.com/dovvnloading/Tree-Graph-MindMap/issues) for an overview of current tasks and bugs.

## License

This project is open-source and available under the MIT License. See the LICENSE file for more details.
