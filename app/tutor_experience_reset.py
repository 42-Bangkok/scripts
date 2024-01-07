from constants.users import TUTORS
from intra.intra import API
from services.console import console
from rich.markdown import Markdown
from rich.progress import track
from rich.prompt import Confirm
import uuid

def main():
    description = Markdown("""# Tutor experience reset script
    This script resets all tutor accounts experiences.
    - reset eval points to 5
    - remove all experiencables
    - change email to xbangkok+d5e7@42bangkok.com
    \n
    It looks throught a to zbangkok, if such user exists, it will reset its status.
    """)

    console.print(description)
    choice = Confirm.ask("Continue?")
    if not choice:
        exit()

    api = API()
    tutors = []
    for tutor in track(TUTORS, description="Getting tutors"):
        try:
            u = api.user(tutor)
            tutors.append(u)
        except:
            console.log(f'\n{tutor} not found')
    console.log(f'{len(tutors)} tutors found')

    # Change email
    console.log("changing email")
    for tutor in track(tutors, description="Changing email"):
        login = tutor.login
        u.change_email(f"{login}+{str(uuid.uuid4())[:4]}@42bangkok.com")
        console.log(f"\n{tutor} email changed")
    console.log("done")

    # Reset all correction points to 5
    console.log("resetting tutors' correction points")
    for tutor in track(tutors, description="Resetting tutors"):
        tutor.set_correction_point(5, reason="Reset tutor's correction points")
        console.log(f"\n{tutor} reset")
    console.log("done")

    # Delete all experiences
    console.log("resetting tutors' expriences")
    for tutor in track(tutors, description="Gathering experience ids"):
        experience_ids = [experience["id"] for experience in tutor.get_experiences()]
        api.delete_experiences(experience_ids)
        console.log(f"\n{tutor} reset")
    console.log("done")

    # Verify
    console.log("verifying")
    status = {
        "success": [],
        "failed": []
    }
    for tutor in track(tutors, description="Verifying"):
        experiences = tutor.get_experiences()
        if len(experiences) != 0 or tutor.correction_point != 5:
            status['failed'].append(tutor.login)
        else:
            status['success'].append(tutor.login)
    console.log(status)
    console.log("done")

if __name__ == "__main__":
    main()
