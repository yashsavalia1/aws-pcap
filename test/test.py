from subprocess import Popen, PIPE, CalledProcessError

cmd = "../packet_capture/netcap_upload"

print("Running..")
with Popen(cmd, shell=True, stdout=PIPE, bufsize=1, universal_newlines=True) as p:
    for line in p.stdout:
        print(line, end='') # process line here

if p.returncode != 0:
    raise CalledProcessError(p.returncode, p.args)