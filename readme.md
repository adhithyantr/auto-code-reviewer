# Automated Code Reviewer & Bug Hunter CLI

A powerful, terminal-based Command Line Interface (CLI) tool that automatically reviews source code, identifies bugs, spots performance bottlenecks, and provides refactoring suggestions. Powered by Google's Gemini API and formatted with rich terminal graphics.

## ✨ Features

- **Automated Code Review**: Sends your source code to the Gemini API for deep analysis.
- **Structured Insights**: Returns a strict, structured report detailing issues by line number, severity, and category.
- **Refactoring Suggestions**: Provides a complete, refactored version of your code with syntax highlighting.
- **Pre-flight Validation**: Automatically rejects non-code files and files larger than 100 KB to save API tokens.
- **Beautiful Terminal Output**: Uses the `rich` library to render executive summaries, issue tables, and colored syntax right in your terminal.
- **Robust Error Handling**: Gracefully handles API rate limits, missing files, and model unavailability without crashing.

## 🛠️ Prerequisites

- Python 3.9+
- A Google Gemini API Key

## 🚀 Installation

1. **Clone or create the project directory:**
   ```bash
   mkdir mittai
   cd mittai
   ```

2. **Set up a virtual environment (Recommended):**
   ```bash
   python -m venv .venv
   
   # On Windows:
   .venv\Scripts\activate
   # On macOS/Linux:
   source .venv/bin/activate
   ```

3. **Install the required dependencies:**
   ```bash
   pip install google-genai pydantic python-dotenv rich
   ```

## ⚙️ Configuration

Create a `.env` file in the root of your project directory and add your Gemini API key:

```env
GEMINI_API_KEY=your_actual_api_key_here
```
*(Make sure there are no spaces around the `=` sign).*

## 💻 Usage

Run the CLI tool by passing the path to the source code file you want to review:

```bash
python app/reviewer.py path/to/your/code.py
```

### Example Test Case

If you run the tool on a file containing bad code (`sample_bad_code.py`), you will see:
1. A brief **Executive Summary** panel.
2. A **Detected Issues & Bottlenecks** table listing bugs (e.g., String concatenation inside loops, potential division by zero).
3. The **Refactored Code** printed with proper syntax highlighting.

## 📁 Project Structure

```text
mittai/
├── .venv/                 # Python virtual environment
├── .env                   # Environment variables (API Key)
├── requirements.txt       # Project dependencies
└── app/
    ├── reviewer.py        # The main CLI application script
    └── sample_bad_code.py     # Sample file for testing
```

## ⚠️ Troubleshooting

- **API Error: 404 NOT_FOUND**: If you see an error that the model is not found, the AI model version might have been deprecated. Open `app/reviewer.py` and update the `model=` parameter (e.g., to `gemini-3.6-flash` or `gemini-1.5-flash`).
- **Missing API Key**: Ensure your `.env` file uses the exact format `GEMINI_API_KEY=value`.