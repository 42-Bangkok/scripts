import os
from services.console import console


def main():
    scripts = [i for i in os.listdir() if i.endswith('.py') and i != 'main.py']
    console.print("""[bold green]Launch which scripts?[/bold green]""")
    console.print("-" * 20)
    for i, script in enumerate(scripts):
        console.print(f"[blue]{i} {script}[/blue]")
    console.print("-" * 20)
    while True:
        choice = console.input("[bold green]Enter the number of the script you want to launch, (e) to exit: [/bold green]")
        if choice == 'e':
            exit()
        try:
            choice = int(choice)
            if choice not in range(0, len(scripts)):
                console.print("[bold red]Invalid input[/bold red]")
                continue
            break
        except ValueError:
            console.print("[bold red]Invalid input[/bold red]")
    os.system(f"python {scripts[choice]}")


if __name__ == '__main__':
    main()
