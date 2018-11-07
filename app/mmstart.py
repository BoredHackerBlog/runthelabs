import mmcontrol as mmc
import dbcontrol
import hashlib, random

def startmm(config): #supply with labconfig
    mmc.start_mm() #Start minimega, use ksm, and kill dnsmasq if already running

    vnc_port_counter = 5899 #Ports after this will get used for VNC

    #Add a gre tunnel
    if config.has_key('gre'):
        for tunnel in config['gre']:
            mmc.setup_gre(tunnel, config['gre'][tunnel])

    #Create a tap then start dnsmasq
    #Tap can expose open ports on the host to the VM's
    if config.has_key('dhcp'):
        for tap in config['dhcp']:
            mmc.dhcp_start(tap, config['dhcp'][tap]['cidr'], config['dhcp'][tap]['tapip'], config['dhcp'][tap]['startip'], config['dhcp'][tap]['endip']) #create a tap from which we can assign IPs and start dnsmasq on that tap

    #Setup traffic forwarding
    if config.has_key('internet'):
        mmc.internet_start(config['internet']['cidr'],config['internet']['outinterface'])

    #Create the VM's
    if config.has_key('vm'):
        for vm in config['vm']:
            vm_name = vm
            vm_memory = config['vm'][vm]['ram']
            vm_disk = config['vm'][vm]['disk']
            vm_net = config['vm'][vm]['network']
            password = hashlib.md5(str(random.random())).hexdigest()[:6] #generate a random password
            vnc_port_counter = vnc_port_counter + 1 #add to vnc_port_counter. This is printed in the password file
            #start configuring minimega VM
            mmc.vm_config(vm_name, vm_memory, vm_disk, vm_net)
            mmc.vm_start(vm_name)
            mmc.set_password(vm_name, password)

            dbcontrol.add_vm(vm_name, password, vnc_port_counter) #Add data to database
