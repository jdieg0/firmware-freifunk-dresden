#!/bin/sh
#creates manually the config because of special wifi ranges
#file is linked via /etc/dnsmasq.conf
# see http://www.faqs.org/rfcs/rfc2132.html for more dhcp options

FINAL=/tmp/resolv.conf.final
AUTO=/tmp/resolv.conf.auto

if [ "$1" = "configure" ]; then
	eval $(/usr/lib/ddmesh/ddmesh-ipcalc.sh -n $(uci get ddmesh.system.node))

	# set domains resolved by freifunk dns
	nameserver="$(uci get ddmesh.network.internal_dns | sed -n '/^[0-9]\+\.[0-9]\+\.[0-9]\+\.[0-9]\+$/p')"
	uci -q set dhcp.dnsmasq.rebind_domain='ffdd/mei'
	uci -q delete dhcp.dnsmasq.server
	if [ -n "$nameserver" ]; then
		uci -q add_list dhcp.dnsmasq.server="/ffdd/$nameserver"
		uci -q add_list dhcp.dnsmasq.server="/mei/$nameserver"
		uci -q add_list dhcp.dnsmasq.server="//#"
	fi

	#don't use 'freifunk-dresden.de' as domain!
	domain=freifunk
	uci -q set dhcp.dnsmasq.domain="$domain"

	# no dns queries from the wan
	uci -q delete dhcp.dnsmasq.notinterface
	uci -q add_list dhcp.dnsmasq.notinterface="$(uci get network.wan.ifname 2>/dev/null)"

	# lan
	if [ "$(uci get ddmesh.network.dhcp_lan_limit)" != 0 ]; then
		#create LAN DHCP: IP,NETMASK,BROADCAST,NETWORK,PREFIX,START,END
		eval $(ipcalc.sh $(uci get network.lan.ipaddr) $(uci get network.lan.netmask) $(uci get ddmesh.network.dhcp_lan_offset) $(uci get ddmesh.network.dhcp_lan_limit))

		test -z "$(uci -q get dhcp.dhcp)" && {                                                 
			uci add dhcp dhcp             
			uci rename dhcp.@dhcp[-1]='lan'
		}                                      

		# start dhcp server also if another server is running in network
		uci -q set dhcp.lan.force='1'

		uci -q set dhcp.lan.interface='lan'	# network, not ifname
		uci -q set dhcp.lan.start="$(uci get ddmesh.network.dhcp_lan_offset)"
		uci -q set dhcp.lan.limit="$(uci get ddmesh.network.dhcp_lan_limit)"
		uci -q set dhcp.lan.leasetime="$(uci get ddmesh.network.dhcp_lan_lease)"
		uci -q delete dhcp.lan.dhcp_option
		uci -q add_list dhcp.lan.dhcp_option="6,$(uci get network.lan.ipaddr)"	# dns
		uci -q add_list dhcp.lan.dhcp_option="3,$(uci get network.lan.ipaddr)"  # default route
		uci -q add_list dhcp.lan.dhcp_option="1,$NETMASK"
		uci -q add_list dhcp.lan.dhcp_option="28,$BROADCAST"
		uci -q add_list dhcp.lan.dhcp_option="12,$_ddmesh_hostname"	# hostname
		uci -q add_list dhcp.lan.dhcp_option="15,$domain"		# domain
		uci -q add_list dhcp.lan.dhcp_option="119,$domain"		# search path
	else
		# disable dhcp on lan
		uci -q delete dhcp.lan
	fi

	# wifi2
	# start dhcp server also if another server is running in network
	uci -q set dhcp.wifi2.force='1'

	uci -q set dhcp.wifi2.interface='wifi2'		# network, not ifname
	uci -q set dhcp.wifi2.start="$_ddmesh_wifi2dhcpstart"
	uci -q set dhcp.wifi2.limit="65534"
	uci -q set dhcp.wifi2.leasetime="$(uci get ddmesh.network.wifi2_dhcplease)"
	uci -q delete dhcp.wifi2.dhcp_option

	dns2=$(uci -q get ddmesh.network.fallback_dns | sed 's#[ 	+]##g')
	test -n "$dns2" && dns2=",$dns2"

	uci -q add_list dhcp.wifi2.dhcp_option="6,$_ddmesh_wifi2ip$dns2"	# dns
	uci -q add_list dhcp.wifi2.dhcp_option="3,$_ddmesh_wifi2ip"  # default route
	uci -q add_list dhcp.wifi2.dhcp_option="1,$_ddmesh_wifi2netmask"
	uci -q add_list dhcp.wifi2.dhcp_option="28,$_ddmesh_wifi2broadcast"
	uci -q add_list dhcp.wifi2.dhcp_option="12,$_ddmesh_hostname"	# hostname
	uci -q add_list dhcp.wifi2.dhcp_option="15,$domain"		# domain
	uci -q add_list dhcp.wifi2.dhcp_option="119,$domain"		# search path

	uci_commit.sh
fi

if [ "$1" == start ]; then
	# link to resolv.conf.auto as long as bmxd has not written resolv.conf.final
	rm -f $FINAL
	ln -s $AUTO $FINAL

	/etc/init.d/dnsmasq stop 2>/dev/null
	/etc/init.d/dnsmasq start 2>/dev/null
fi

