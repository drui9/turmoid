from Droid.termux import Termux
from Droid import droid


# -- start--
@Termux.arg()
def whoami(cmd :str):
	return droid.termux.execute(cmd).strip('\n')
