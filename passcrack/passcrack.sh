#!/bin/bash

# User input
keyid=$1
passfile=$2

# Tunables
sdelta=5
cdelta=10
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
