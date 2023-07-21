from Droid.termux import Termux
from Droid import termux


# -- start--
@Termux.arg()
def whoami(cmd :str):
	return termux.execute(cmd).strip('\n')
