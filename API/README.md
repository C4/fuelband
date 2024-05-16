# DNS Setup

This configures a *very limited* DNS server to route the API requests. This assumes running on Ubuntu 22.04 or similar. 

## Install DNSMASQ

```sudo apt install dnsmasq```

Reboot if needed.

Next, grab your external IP address.
```dig +short txt ch whoami.cloudflare @1.0.0.1```

Then edit the dnsmasq config file...
```sudo vim /etc/dnsmasq.conf```

search and uncomment / add lines and replace your external IP with the one you just grabbed.

```
no-resolv
strict-order
address=/nike.com/{yourexternalIPaddress}
```

Next, edit the the service to allow for external connections.
Edit: 
```/etc/init.d/dnsmasq``` 
and remove `--local-service` from `DNSMASQ_OPTS`

The systemd-resolved will interfere with running dnsmasq so you need to disable it.

```
sudo systemctl stop systemd-resolved 
sudo systemctl disable systemd-resolved 
sudo systemctl mask systemd-resolved
```

Incase you need to undo what you did:

```
sudo systemctl unmask systemd-resolved 
sudo systemctl enable systemd-resolved 
sudo systemctl start systemd-resolved
```

Start dnsmasq
```systemctl start dnsmasq.service```

Check if it's running
```systemctl status dnsmasq.service```

The DNS part should be good to go now. You can test by setting your DNS server to the IP address and digging for nike.com