import os
from rich.markdown import Markdown
from rich.progress import track
from intra.intra import API
from services.console import console
from services.inputs import get_logins
from rich.prompt import Confirm


def main():
    description = Markdown("""# Reset user's evaluation point
    This resets a user's evaluation points.
    - reset eval points to 3
    \n
    check app/inputs/reset_eval_pts.csv.sample for the input format\n
    """
    )
    console.print(description)
    if not os.path.exists("inputs/reset_eval_pts.csv"):
        console.print(
            "[bold red]app/inputs/reset_eval_pts.csv not found[/bold red]"
        )
        exit()
    logins = get_logins("inputs/reset_eval_pts.csv")
    console.print(f"The script will alter {len(logins)} users: {', '.join(logins)}")
    console.print("Make sure the input is correct.")
    choice = Confirm.ask("Continue?")
    if not choice:
        exit()

    api = API()
    # set correction points
    users = []
    for login in track(
        logins,
        description="Getting users",
    ):
        try:
            u = api.user(login)
            users.append(u)
        except:
            console.log(f"\n{login} not found")
    console.log(f"{len(users)} users found")

    for user in track(users, description="Resetting users"):
        user.set_correction_point(3, reason="reset evaluation point", refresh=False)
        console.log(f"\n{user} reset")
    console.log("done")

    # validate correction points
    for login in track(
        logins,
        description="Validating users",
    ):
        u = api.user(login)
        if u.correction_point != 3:
            console.log(f"{u} not reset")
    console.log("done")

if __name__ == "__main__":
    main()
