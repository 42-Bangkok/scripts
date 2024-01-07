from rich.markdown import Markdown
from rich.progress import track
from rich.prompt import Confirm

description = Markdown("""# Reset user's evaluation point
This resets a user's evaluation points.
- reset eval points to 3
\n
check app/inputs/reset_eval_pts.csv.sample for the input format\n
""")
