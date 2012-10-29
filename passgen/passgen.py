#!/usr/bin/python
# -*- coding: utf-8 -*-
#
# passgen - A password generator suitable for feeding brute-force crackers
#
#    Copyright (C) 2012 Rodrigo Silva (MestreLion) <linux@rodrigosilva.com>
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program. See <http://www.gnu.org/licenses/gpl.html>


import sys
import itertools
import argparse
import logging as logger
from math import log, ceil, factorial as fac

def totalguess(v, n, n0=1):
    return sum([int(ceil(v**r)) * fac(n) / fac(n-r)
                for r in range(n0, n+1)])

def roundmag(x, n):
    return int(round(x, n - int(log(x, 10)) -1))

def geomean(numlist):
    return (reduce(lambda x, y: x*y, numlist, 1))**(1.0/len(numlist))

def humantime(s):
    c = 3
    m = 60
    h = 60 * m
    d = 24 * h
    w =  7 * d
    M =  4 * w
    y = 12 * M

    if s < c*m: return "%d seconds" %  s
    if s < c*h: return "%d minutes" % (s/m)
    if s < c*d: return "%d hours"   % (s/h)
    if s < c*w: return "%d days"    % (s/d)
    if s < c*M: return "%d weeks"   % (s/w)
    if s < c*y: return "%d months"  % (s/M)
    return             "%d years"   % (s/y)

def feedback(total):
    log.info("{:,} passwords written".format(total))

def parseargs():
    parser = argparse.ArgumentParser(
        description='Generate passwords from a template. '
                    'Suitable for feeding brute-force crackers like passcrack')

    parser.add_argument('--quiet', '-q', dest='verbose',
                        default=True,
                        action='store_false',
                        help='suppress informative messages.')

    parser.add_argument('--max', '-x', dest='maxterms',
                        default=0, type=int,
                        help='maximum number of terms.')

    parser.add_argument('--min', '-n', dest='minterms',
                        default=1, type=int,
                        help='minimum number of terms.')

    parser.add_argument('--delimiter', '-d', dest='delimiter',
                        default='\t',
                        help='field delimiter in template file. Default is TAB.')

    parser.add_argument('infile',
                        nargs='?',
                        help='input template file . Default is standard input.')

    parser.add_argument('outfile',
                        nargs='?',
                        help='output password file. Default is standard output.')

    return parser.parse_args()


if __name__ == "__main__":

    args = parseargs()

    logger.basicConfig(level=logger.INFO if args.verbose else logger.ERROR,
                       format='%(asctime)s: %(message)s')


    search = []
    with open(args.infile) if args.infile else sys.stdin as f:
        for input in f:
            if input[:-1]: search.append(set(input[:-1].split(args.delimiter)))

    if not search:
        logger.error("Empty template file!")
        sys.exit(1)

    args.maxterms = args.maxterms or len(search)

    # Print input statistics
    num_variations = [len(t) for t in search]
    tot_variations = sum(num_variations)
    logger.info("Input: {:,} terms, {:,} total variations"
                "".format(len(search), tot_variations))

    # Print output estimations
    variations_geomean = geomean(num_variations)
    variations_avgsize = sum([len(v) for t in search for v in t])/tot_variations
    guess = totalguess(variations_geomean, args.maxterms, args.minterms)
    logger.info("Output estimative: ~{:,} passwords, {:,} KiB, {} at 1MiB/s"
                "".format(roundmag(guess, 3),
                          roundmag(float(variations_avgsize *
                                       args.maxterms *
                                       guess / 1000), 2),
                          humantime(guess / (10**6))))

    total = 0
    with open(args.outfile, 'w') if args.outfile else sys.stdout as f:
        try:
            for r in range(args.minterms, args.maxterms+1):
                for p in itertools.permutations(search, r):
                    for pwd in itertools.product(*p):
                        f.write("%s\n" % "".join(pwd))
                        total += 1
        except KeyboardInterrupt:
            pass
        finally:
            logger.info("{:,} total passwords written".format(total))
