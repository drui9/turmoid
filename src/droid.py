"""Upgrade procedure
if running
    if dependencies changed
        - reinstall dependencies
else if not running
    if dependencies changed
        - reinstall dependencies
"""
from droid import Droid


db = Droid()
db.scheduler()
