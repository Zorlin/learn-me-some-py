#!/usr/bin/env python3
"""
End-to-end test: Load hello_world challenge and present it beautifully.

This demonstrates the complete vertical slice:
1. Load challenge from TOML
2. Display challenge beautifully with Rich
3. Execute user code safely
4. Show test results with visual feedback (✓/✗)
"""

from pathlib import Path
from rich.console import Console

from lmsp.python.challenges import ChallengeLoader
from lmsp.python.presenter import ChallengePresenter

def main():
    console = Console()

    # 1. Load challenge from TOML
    console.print("\n[bold cyan]Step 1: Loading challenge from TOML...[/]")
    challenges_dir = Path(__file__).parent / "challenges"
    loader = ChallengeLoader(challenges_dir)

    challenge = loader.load("hello_world")
    console.print(f"[green]✓[/] Loaded challenge: {challenge.name}")

    # 2. Display challenge beautifully
    console.print("\n[bold cyan]Step 2: Displaying challenge with Rich panels...[/]")
    presenter = ChallengePresenter(console)
    presenter.display_challenge(challenge)
    presenter.display_skeleton(challenge)

    # 3. Test with correct solution
    console.print("\n[bold cyan]Step 3: Testing correct solution...[/]")
    correct_code = 'print("Hello, World!")'
    results = presenter.execute_code(correct_code, challenge)
    presenter.display_results(results, challenge)

    # 4. Test with incorrect solution
    console.print("\n[bold cyan]Step 4: Testing incorrect solution...[/]")
    wrong_code = 'print("Hello World")'  # Missing comma and exclamation
    results = presenter.execute_code(wrong_code, challenge)
    presenter.display_results(results, challenge)

    # 5. Test with syntax error
    console.print("\n[bold cyan]Step 5: Testing code with syntax error...[/]")
    syntax_error_code = 'print("Hello, World!'  # Missing closing quote
    results = presenter.execute_code(syntax_error_code, challenge)
    presenter.display_results(results, challenge)

    console.print("\n[bold green]✨ End-to-end test complete! All features working beautifully. ✨[/]\n")

if __name__ == "__main__":
    main()
