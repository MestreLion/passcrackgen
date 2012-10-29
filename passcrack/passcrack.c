/*
 * Passcrack - a simple GPG passphrase cracker based on Rephrase and Nasty
 *
 * Copyright (C) 2012 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
 * Portions Copyright (C) 2003 Phil Lanch <phil@subtle.clara.co.uk>
 * Portions Copyright (C) 2005 Folkert van Heusden <folkert@vanheusden.com>
 *
 * This program is free software: you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation, either version 3 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program. See <http://www.gnu.org/licenses/gpl.html>
 */

#include <sys/mman.h>
#include <sys/types.h>
#include <sys/wait.h>
#include <sys/stat.h>
#include <errno.h>
#include <fcntl.h>
#include <stdio.h>
#include <stdlib.h>
#include <termios.h>
#include <unistd.h>

#define PROGRAM "passcrack"
#define VERSION "1.0"

#ifndef GPG
#define GPG "/usr/bin/gpg"
#endif

int
main (int argc, char **argv)
{
  struct secrets sec;
  struct stat stat_buf;

  fprintf (stderr, "%s (Passcrack) %s\nCopyright (C) 2012  Rodrigo Silva\n"
      "This program comes with ABSOLUTELY NO WARRANTY.\n"
      "This is free software, and you are welcome to redistribute it\n"
      "under the GNU Public License, version 3 or later.\n\n",
      PROGRAM, VERSION);

  if (mlock (&sec, sizeof (struct secrets))) {
    perror ("mlock: ");
    fprintf (stderr, "(%s should be installed setuid root)\n", PROGRAM);
    exit (2);
  }
  if (setreuid (getuid (), getuid ())) {
    perror ("setreuid: ");
    exit (3);
  }

  if (stat (GPG, &stat_buf)) {
    if (errno & (ENOENT | ENOTDIR)) {
      fprintf (stderr, "%s does not exist (or is in a directory I cannot read)"
          "\n(perhaps you need to redefine GPG and recompile)\n", GPG);
      exit (4);
    }
    perror ("stat: ");
    exit (5);
  }
  if (!S_ISREG(stat_buf.st_mode)
      || !(stat_buf.st_mode & (stat_buf.st_uid == getuid () ? S_IXUSR
      : stat_buf.st_gid == getgid () ? S_IXGRP : S_IXOTH))) {
    fprintf (stderr, "%s is not an executable (by me) file\n", GPG);
    exit (6);
  }

  if (argc != 2) {
    fprintf (stderr, "Usage: %s <key> [passwords file]\n", PROGRAM);
    exit (7);
  }

  puts("!!!Hello World!!!"); /* prints !!!Hello World!!! */
  return EXIT_SUCCESS;
}
