from Droid.termux import Termux


# -- start--
@Termux.arg()
def whoami(output):
	return output.strip('\n')
