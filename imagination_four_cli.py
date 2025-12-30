import argparse
from imagination_four import run_444

def parse_imagination(argv):
    p = argparse.ArgumentParser(add_help=False)
    p.add_argument("--im", action="store_true", help="enable imagination* gate")
    p.add_argument("--im-timeout", type=int, default=4, help="seconds per gate (default 4)")
    p.add_argument("--im-ego", action="store_true", help="print failures (off by default)")
    args, rest = p.parse_known_args(argv)
    return args, rest

def run_if_enabled(argv):
    args, rest = parse_imagination(argv)
    if args.im:
        r = run_444(args.im_timeout)
        if args.im_ego:
            print(r)
        if r["code"] in ("defer","abort"):
            raise SystemExit(1)
    return rest
