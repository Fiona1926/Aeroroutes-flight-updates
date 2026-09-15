# chat.py
from rich.console import Console
from rag_system import rag_chain

console = Console()


def main():
    console.rule("[bold cyan]Flight Log RAG Chatbot")
    console.print("[dim]Type 'exit' or 'quit' to leave.[/dim]")
    console.rule(style="cyan")

    while True:
        try:
            user_input = console.input("\n[bold cyan]You:[/bold cyan] ").strip()    #closing [/...] to change color midway
        except (EOFError, KeyboardInterrupt):
            console.print("\n[bold]Bye![/bold]")
            break

        if not user_input:
            continue
        if user_input.lower() in {"exit", "quit"}:
            console.print("[bold]Bye![/bold]")
            break

        try:
            result = rag_chain.invoke({"input": user_input})
        except Exception as e:
            console.print(f"\n[bold red]\\[error][/bold red] {e}")
            continue

        answer = result["answer"]
        console.print(f"\n[bold green]Bot:[/bold green] {answer}")


if __name__ == "__main__":
    main()