from Droid.termux import Termux
from Droid import termux

# -- start --
@Termux.arg()
@Termux.arg('-h')
def termux_audio_info(cmd :str):
	"""Get information about audio capabilities."""
	return termux.execute(cmd)
