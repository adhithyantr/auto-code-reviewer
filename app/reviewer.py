import os
import sys
import argparse
from pathlib import Path
from pydantic import BaseModel, Field
from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.table import Table

# Import the official Google Gen AI SDK
from google import genai
from google.genai import types
from google.genai.errors import APIError

# Initialize Rich Console for beautiful terminal outputs
console = Console()

# ---------------------------------------------------------------------------
# 1. STRUCTURED OUTPUT SCHEMA (PYDANTIC)
# ---------------------------------------------------------------------------
class Issue(BaseModel):
    line_number: int = Field(description="The line number where the issue occurs")
    severity: str = Field(description="Severity of the issue: 'low', 'medium', or 'high'")
    category: str = Field(description="Category (e.g., 'Bug', 'Performance', 'Security')")
    description: str = Field(description="Detailed explanation of the issue")

class CodeReviewReport(BaseModel):
    summary: str = Field(description="Brief overall opinion of the code")
    issues: list[Issue] = Field(description="List of identified issues")
    refactored_code: str = Field(description="Improved and fully refactored version of the input file")

# ---------------------------------------------------------------------------
# 2. FILE VALIDATION LOGIC
# ---------------------------------------------------------------------------
ALLOWED_EXTENSIONS = {'.py', '.js', '.ts', '.cpp', '.c', '.java', '.cs', '.go', '.rs', '.php'}
MAX_FILE_SIZE_KB = 100

def validate_file(file_path: Path) -> str:
    """Validates if the file exists, is a valid code file, and is under the size limit."""
    if not file_path.exists():
        console.print(f"[bold red]Error:[/bold red] File '{file_path}' does not exist.")
        sys.exit(1)
        
    if not file_path.is_file():
        console.print(f"[bold red]Error:[/bold red] '{file_path}' is not a valid file.")
        sys.exit(1)

    if file_path.suffix.lower() not in ALLOWED_EXTENSIONS:
        console.print(f"[bold red]Error:[/bold red] Unsupported file type '{file_path.suffix}'. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}")
        sys.exit(1)

    file_size_kb = os.path.getsize(file_path) / 1024
    if file_size_kb > MAX_FILE_SIZE_KB:
        console.print(f"[bold red]Error:[/bold red] File is too large ({file_size_kb:.2f} KB). Maximum allowed size is {MAX_FILE_SIZE_KB} KB.")
        sys.exit(1)

    with open(file_path, 'r', encoding='utf-8') as f:
        return f.read()

# ---------------------------------------------------------------------------
# 3. GEMINI API INTEGRATION & ERROR HANDLING
# ---------------------------------------------------------------------------
def review_code(code_content: str):
    """Sends the code to Gemini and retrieves the structured JSON response."""
    # Load environment variables safely
    load_dotenv()
    api_key = os.environ.get("GEMINI_API_KEY")
    
    if not api_key:
        console.print("[bold red]Error:[/bold red] GEMINI_API_KEY environment variable not found. Please check your .env file.")
        sys.exit(1)

    client = genai.Client(api_key=api_key)

    prompt = f"""
    You are an expert Senior Software Engineer. Review the following source code.
    Identify bugs, performance bottlenecks, and provide refactoring suggestions.
    Return the response STRICTLY matching the requested JSON schema.
    
    Code to review:
    \n\n{code_content}
    """

    try:
        with console.status("[bold cyan]Analyzing code and hunting bugs...", spinner="dots"):
            response = client.models.generate_content(
                model='gemini-3.6-flash',
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=CodeReviewReport,
                    temperature=0.2, # Low temperature for more analytical/deterministic output
                ),
            )
            
            # The SDK automatically parses the JSON back into our Pydantic model structure if requested,
            # or we can parse the raw JSON string. Since we used response_schema, the text is guaranteed JSON.
            import json
            report_data = json.loads(response.text)
            return report_data
            
    except APIError as e:
        console.print(f"\n[bold red]API Error:[/bold red] Failed to communicate with Gemini. Details: {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"\n[bold red]Unexpected Error:[/bold red] {e}")
        sys.exit(1)

# ---------------------------------------------------------------------------
# 4. RESPONSE RENDERING
# ---------------------------------------------------------------------------
def display_report(report_data: dict, file_ext: str):
    """Formats and prints the report nicely in the terminal."""
    console.print("\n[bold green]✅ Code Review Complete![/bold green]\n")
    
    # 1. Summary Panel
    console.print(Panel(report_data.get('summary', 'No summary provided.'), title="[bold blue]Executive Summary", border_style="blue"))
    
    # 2. Issues Table
    issues = report_data.get('issues', [])
    if issues:
        table = Table(title="Detected Issues & Bottlenecks", show_header=True, header_style="bold magenta")
        table.add_column("Line", justify="right", style="cyan", no_wrap=True)
        table.add_column("Severity", justify="center")
        table.add_column("Category", style="yellow")
        table.add_column("Description")

        for issue in issues:
            severity = issue.get('severity', '').lower()
            if severity == 'high':
                sev_styled = "[bold red]HIGH[/bold red]"
            elif severity == 'medium':
                sev_styled = "[bold yellow]MEDIUM[/bold yellow]"
            else:
                sev_styled = "[bold green]LOW[/bold green]"
                
            table.add_row(
                str(issue.get('line_number', 'N/A')),
                sev_styled,
                issue.get('category', 'N/A'),
                issue.get('description', 'N/A')
            )
        console.print("\n")
        console.print(table)
    else:
        console.print("\n[bold green]No major issues found! Great job.[/bold green]")

    # 3. Refactored Code
    console.print("\n[bold blue]### Refactored Code Suggestion ###[/bold blue]")
    # Map the file extension to a Pygments lexer for syntax highlighting
    lexer_map = {'.py': 'python', '.js': 'javascript', '.ts': 'typescript', '.cpp': 'cpp'}
    lexer = lexer_map.get(file_ext, 'python')
    
    syntax = Syntax(report_data.get('refactored_code', ''), lexer, theme="monokai", line_numbers=True)
    console.print(syntax)

# ---------------------------------------------------------------------------
# MAIN CLI ENTRY POINT
# ---------------------------------------------------------------------------
def main():
    parser = argparse.ArgumentParser(description="Automated Code Reviewer & Bug Hunter CLI")
    parser.add_argument("file", help="Path to the source code file to review")
    args = parser.parse_args()

    file_path = Path(args.file)
    
    # Process
    code_content = validate_file(file_path)
    report_data = review_code(code_content)
    display_report(report_data, file_path.suffix.lower())

if __name__ == "__main__":
    main()