minimega_path = "/root/mm" #Full path to minimega binary
websockify_run = "/home/research/runthelabs/API/websockify/run" #websockify run file
#Command to change VNC password use %password to give it the password
pwcmd = """'{ "execute": "change", "arguments": { "device": "vnc", "target": "password", "arg": "%s" } }'"""

minimega_start = minimega_path + " -nostdin &" #Command to start minimega with -nostdin
minimega_cmd = minimega_path + " -e " #Since we're not using stdin, we'll have to use -e to pass commands to minimega
