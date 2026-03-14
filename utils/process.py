# Source - https://stackoverflow.com/a/64707896
# Posted by mg34, modified by community. See post 'Timeline' for change history
# Retrieved 2026-03-07, License - CC BY-SA 4.0

import subprocess
def process_exists(process_name):
    progs = str(subprocess.check_output('tasklist'))
    if process_name in progs:
        return True
    else:
        return False
