# -*- coding:utf-8 -*-
import sys
from pyramid.paster import bootstrap
import itertools


def err(x):
    sys.stderr.write(x)
    sys.stderr.write("\n")


def tree_writer(itr, xs=[None, None, None, None]):
    mapped = ["", "", "", ""]
    for ys in itr:
        for i, (x, y) in enumerate(zip(xs[:-1], ys[:-1])):
            if x != y:
                mapped[i] = str(y)
            else:
                mapped[i] = ""
            xs[i] = y
        mapped[-1] = " ".join(str(e) for e in ys[-1])[:60]
        yield "{:<10} {:<10} {:>2} {:<60}".format(*mapped)


def main(argv=sys.argv):
    if len(argv) < 2:
        err("pmapping <config file>")
    if len(argv) > 2:
        filter_word = argv[2]
    else:
        filter_word = None
    configfile = argv[1]

    env = bootstrap(configfile)

    # (model, name, order, (val, order))
    gen = iter(env["registry"].modelaction_list)
    if filter_word:
        gen = (xs for xs in gen if filter_word in xs[3][0])

    print("{:<10} {:<10} {:>2} {:<60}".format("model", "name", "pr", "value"))
    print("-" * 82)

    for line in tree_writer(sorted(gen, key=lambda x: (x[0], x[1], x[2], x[3][0]))):
        print(line)
