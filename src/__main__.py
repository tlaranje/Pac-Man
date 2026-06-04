from src.visualizer import Manager
from rich import print
# import traceback

if __name__ == "__main__":
    try:
        manager = Manager()
        manager.run()
    except Exception as e:
        print(f"[bold red]{e}[/bold red]")
        # traceback.print_exc()
