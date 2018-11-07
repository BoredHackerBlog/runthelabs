from config import minimega_start, minimega_cmd, pwcmd
import os, json
from time import sleep

def stop_mm():
    os.system("iptables-restore < iptables_old") #restore iptables rules
    os.system(minimega_cmd + "nuke") #run the nuke command to stop everything

def start_mm(): #This has to be called first
    os.system(minimega_start) #Start minimega
    sleep(5) #wait for it to start

    os.system(minimega_cmd + "optimize ksm true") #use ksm, it helps with memory
    #os.system(minimega_cmd + "optimize affinity true")
    os.system("killall dnsmasq") #kill dnsmasq if already running

def dhcp_start(tap, cidr, tapip, startip, endip):
    os.system(minimega_cmd + "tap create %s ip %s"%(tap,cidr,)) #create a tap from which we can assign IP's
    os.system(minimega_cmd + "dnsmasq start %s %s %s"%(tapip,startip,endip,)) #start dnsmasq on that tap

def internet_start(cidr, outinterface):
    os.system("iptables-save > iptables_old") #save iptables rules
    os.system("echo 1 | tee -a /proc/sys/net/ipv4/ip_forward") #enable ipv4 ip forwarding
    os.system("sysctl -w net.ipv4.ip_forward=1")
    os.system("iptables -t nat -A POSTROUTING -o %s -s %s -j MASQUERADE"%(outinterface,cidr,)) #setup iptables
    os.system("iptables -P FORWARD DROP")
    os.system("iptables -A FORWARD -m state --state RELATED,ESTABLISHED -j ACCEPT")
    os.system("iptables -A FORWARD -s %s -j ACCEPT"%(cidr,))
    os.system("iptables -A FORWARD -s %s -d %s -j ACCEPT"%(cidr,cidr,))

def vm_config(vm_name, vm_memory, vm_disk, vm_net):
    os.system(minimega_cmd + "vm config net "+ vm_net) #network
    os.system(minimega_cmd + "vm config memory " + vm_memory)
    os.system(minimega_cmd + "vm config disk "+ vm_disk)
    os.system(minimega_cmd + "vm launch " + vm_name) #launch in a paused state

def vm_start(vm_name): #This is called after vm_config
    os.system(minimega_cmd + "vm start " + vm_name) #start

def set_password(vm_name, password):#This can be called before vm_start or after vm_config
    vncpwcmd=pwcmd%password
    os.system(minimega_cmd + "vm qmp " + vm_name + " " + json.dumps(vncpwcmd)) #set password for that VM

def vm_reboot(vm_name, password):
    os.system(minimega_cmd + "vm kill " + vm_name) #Kill the VM
    os.system(minimega_cmd + "vm start " + vm_name) #Start the VM
    vncpwcmd=pwcmd%password
    os.system(minimega_cmd + "vm qmp " + vm_name + " " + json.dumps(vncpwcmd)) #set password for that VM

def vm_stop(vm_name):
    os.system(minimega_cmd + "vm kill " + vm_name) #Kill the VM

def setup_gre(tunnel_name, tunnel_ip): #Set up GRE tunnel with another machine. The other machine also has to run the same command (with different IP...)
    os.system("ovs-vsctl add-port mega_bridge %s -- set interface %s type=gre options:remote_ip=%s"%(tunnel_name, tunnel_name,tunnel_ip,))
