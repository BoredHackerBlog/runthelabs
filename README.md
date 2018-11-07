Read Documenation!

This project is very similar to this: https://github.com/BoredHackerBlog/json2labs/

Use install.sh to install everything. Run as root.

Edit config.py and point to the correct minimega binary location.

Run api.py and visit https://localhost:1337/webui or use the API. Default login is admin/admin but you can modify api.py to change that.

Generate configurations using generate_config.py

look at API_README to learn more about how to use the API

This project uses:

minimega: http://minimega.org/ https://github.com/sandia-minimega/minimega

NoVNC: https://novnc.com/info.html https://github.com/novnc/noVNC

Websockify: https://github.com/novnc/websockify

Python 2.7, Flask, qemu-kvm, and openvswitch.

Disclaimer: The code and documentation has not been updated since summer of 2018.