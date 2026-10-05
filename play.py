import os,sys
print(os.getpid(),flush=True)
exec(sys.stdin.read())
