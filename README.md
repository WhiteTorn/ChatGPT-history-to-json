# ChatGPT / HTML Chat Exporter to JSON

A Python script to extract chat conversation history from HTML files (typically exported from platforms like ChatGPT) and convert it into a structured JSON format. It also includes an attempt to preserve Markdown formatting for assistant messages.

The script is multilingual, with console messages available in English (en) and Georgian (ka).

## Features

*   Extracts user and assistant messages from HTML chat exports.
*   Outputs the conversation into a clean, structured JSON file.
*   Attempts to parse and reformat assistant's Markdown content (paragraphs, code blocks, lists, headers, blockquotes, tables, horizontal rules).
*   Supports CLI arguments for input HTML file, output JSON file, and language selection for script messages.
*   Provides basic verification of the extracted data.
*   Includes a fallback mechanism for slightly different HTML structures.

## Requirements

*   Python 3.6+
*   Beautiful Soup 4 (`beautifulsoup4`)

## Installation

1.  **Clone the repository (or download the script):**
    ```bash
    git clone https://github.com/YOUR_USERNAME/YOUR_REPOSITORY_NAME.git
    cd YOUR_REPOSITORY_NAME
    ```
    (Replace `YOUR_USERNAME/YOUR_REPOSITORY_NAME` with your actual GitHub username and repository name.)

2.  **Install dependencies:**
    It's recommended to use a virtual environment:
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```
    Then install the required package:
    ```bash
    pip install -r requirements.txt
    ```
    If you don't have `requirements.txt` yet, you can just run:
    ```bash
    pip install beautifulsoup4
    ```

## Usage

Run the script from your command line / terminal.

**Basic Usage:**

```bash
python chat_extractor.py <input_html_file_path> [options]