Deprecated in favor of this gist: https://gist.github.com/violet4/3d8b139201131ef54da71f386ee5d4ec

* Uses syncoid (sanoid) https://github.com/jimsalterjrs/sanoid
* Creates dedicated permissions-restricted system-level users on both the source and destination machines.
* SSH keys from source to destination
* Passwordless sudo for minimum list of necessary commands
* Automatically pushes (or pulls, if you reconfigure it to pull) all intermediate snapshots.

This was a cute little script, but syncoid is everything this script has, plus more, plus experience from people who actually know what they're doing, plus time and multiple versions of fixes/improvements, increasing its reliability compared to this cute little script.
