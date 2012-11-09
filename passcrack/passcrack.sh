#!/bin/bash
#
# Passcrack - a simple GPG passphrase cracker
#
# Copyright (C) 2012 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program. See <http://www.gnu.org/licenses/gpl.html>
#
# TODO:
# - proper arg parsing
# - convert to python. gpg call can be:
#     - os.system() / subprocess.popen()
#     - one of many python's-gnupg wrappers
# - convert to C. gpg call can be:
#     - gpgme library (nasty approach)
#     - shellexecute() (rephrase approach)
# - integrate with passgen


# User input
keyid=$1
passfile=$2

# Tunables
sdelta=60
cdelta=100
log=$HOME/.passcrack.log

start=$(date +%s)
prev=$start
total=0
count=0
procs=0
tries=0

crack() {
	gpg --default-key "$keyid" --passphrase "$1" --batch --dry-run \
		--no-use-agent --clearsign /dev/null >/dev/null 2>&1 &&
	{
		echo "Password found! :D \o/"
		printf "%s\t%s\t%s\n" "$(date +'%F %T')" "$keymsg" "$password" >> "$log"
		return 0
	}
	return 1
}

usage() { printf "%s\nUsage: passcrack <keyid> <password file>\n" "$1"; exit 1; }

[[ "$keyid" ]]       || usage "No key ID!"

keymsg=$(gpg --list-secret-keys --with-colons "$keyid" | head -n1)
feedback="%s: tried %d (%d passwords/sec). Total: %d, last: %s\n"

printf "Password Cracker\nCracking %s\nUsing %s\n" "$keymsg" "$passfile"
printf "Status feedback every %d seconds\n" "$sdelta"
while read -r password; do

	crack "$password" && exit
	((count++))

	# feedback every 'cdelta' tries and 'sdelta' seconds
	if (( count >= cdelta )); then
		printf -v now '%(%s)T' -1 #now=$(date +%s)
		((tries += count))
		if ((now - prev >= sdelta)); then
			((total += tries))
			printf "$feedback" "$(date +'%F %T')" "$tries" \
				"$((tries/(now - prev)))" "$total" "$password"
			((prev = now, tries = 0))
		fi
		((count = 0))
	fi

done < "$passfile"

echo "Password not found :("
exit 2
