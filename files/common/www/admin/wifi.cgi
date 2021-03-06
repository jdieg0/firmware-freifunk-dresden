#!/bin/sh

export TITLE="Verwaltung > Konfiguration: WIFI"

. /usr/lib/www/page-pre.sh ${0%/*}

cat<<EOF
<h2>$TITLE</h2>
<br>
EOF

if [ -z "$QUERY_STRING" ]; then

if [ "$(uci -q get ddmesh.network.wifi3_network)" = "wan" ]; then
	checked_wan='checked="checked"'
else
	checked_lan='checked="checked"'
fi

# workaround to pass key with " and ' to input field
# javascript setWifi3_key reads content and assigns it to value of input field
wifi3_key="$(uci get credentials.wifi.private_key)"
echo "<div style=\"visibility: hidden;\" id=\"wifi3_key\">$wifi3_key</div>"

cat<<EOM
<div id="status"></div>
<script type="text/javascript">
function disable_fields(s) {
	var c=document.getElementsByName('form_wifi_diversity')[0].checked;
	document.getElementsByName('form_wifi_rxantenna')[0].disabled=c;
	document.getElementsByName('form_wifi_txantenna')[0].disabled=c;
}
function enable_custom_essid(s) {
	var c=document.getElementsByName('form_wifi_custom_essid')[0].checked;
	document.getElementsByName('form_wifi_ap_ssid')[0].disabled= !c;
}
function enable_private_wifi(s) {
	var c=document.getElementsByName('form_wifi3_enabled')[0].checked;
	document.getElementsByName('form_wifi3_ssid')[0].disabled= !c;
	document.getElementsByName('form_wifi3_key')[0].disabled= !c;
	document.getElementsByName('form_wifi3_security_open')[0].disabled= !c;
}
function setWifi3_key()
{
	var k = document.getElementById('wifi3_key');
	//use textContent because innerText is empty when div is invisible
	document.getElementById('id_wifi3_key').value = k.textContent;
}
function checkInput()
{
	var enabled = document.getElementById('id_wifi3_enabled').checked;
	if(enabled)
	{
		var key = document.getElementById('id_wifi3_key').value;
		var ssid = document.getElementById('id_wifi3_ssid').value;
		if( key === undefined || ssid === undefined
		   || key.length < 8 || !checkWifiKey(document.getElementById('id_wifi3_key').value))
		{
			alert("Ungültige WiFi-Konfiguration!\nWiFi-Key/-SSID zu kurz oder enthält ungültige Zeichen.");
			return false;
		}
	}
	return true;
}
</script>

<form onsubmit="return checkInput();" name="form_wifi" action="wifi.cgi" class="form" method="POST">
<fieldset class="bubble">
<legend>WiFi-Einstellungen</legend>
<table>

<tr><th>Freifunk-IP-Adresse:</th>
<td><input name="form_wifi_ip" size="32" type="text" value="$_ddmesh_ip" disabled></td>
</tr>

<tr><th>Freifunk-Netzmaske:</th>
<td><input name="form_wifi_netmask" size="32" type="text" value="$_ddmesh_netmask" disabled></td>
</tr>

<tr><th>Kanal:</th>
<td><input name="form_wifi_channel" size="32" type="text" value="$(uci get ddmesh.network.wifi_channel)" disabled></td>
</tr>

<tr><th>TX-Power:</th>
<td><select name="form_wifi_txpower" size="1">
$(iwinfo $wifi_ifname txpowerlist | awk '{if(match($1,"*")){sel="selected";v=$2;txt=$0}else{sel="";v=$1;txt=$0}; print "<option "sel" value=\""v"\">"txt"</option>"}')
</select> (konfiguriert: $(uci get ddmesh.network.wifi_txpower) dBm) <b>Aktuell:</b> $(iw $wifi_ifname info | awk '/txpower/{print $2,$3}')</td>
</tr>
<tr><td></td><td><font color="red">Falsche oder zu hohe Werte k&ouml;nnen den Router zerst&ouml;ren!</font></td></tr>

<!--
<tr><th>Antenne:</th>
<td><input onchange="disable_fields();" name="form_wifi_diversity" type="CHECKBOX" value="1" $(if [ "$(uci get ddmesh.network.wifi_diversity)" != "0" ];then echo ' checked="checked"';fi)>Automatisch</td>
</tr>
<tr><th></th><td>RX Antenne (Maske): <input name="form_wifi_rxantenna" size="2" MAXLENGTH="1" type="text" value="$(uci get ddmesh.network.wifi_rxantenna )" onkeypress="return isNumberKey(event)"></td></tr>
<tr><th></th><td>TX Antenne (Maske): <input name="form_wifi_txantenna" size="2" MAXLENGTH="1" type="text" value="$(uci get ddmesh.network.wifi_txantenna )" onkeypress="return isNumberKey(event)"></td></tr>
<tr><th></th><td>Bit-Maske: jedes bit steht f&uuml;r eine Antenne. z.B.: 1:Antenne 1; 2:Antenne 2; 4:Antenne 3;<br /> Oder 3:Antennen 1+2; 5-Antennen 1+3; 6:Antennen 2+3; 7:Antennen 1+2+3 </td></tr>
-->
<!-- distance, beacon_int, basic_rate -->


<tr><th>Ad-hoc-SSID:</th>
<td><input name="form_wifi_adhoc_ssid" size="32" type="text" value="$(uci get wireless.@wifi-iface[0].ssid)" disabled></td>
</tr>

<tr><th>BSSID:</th>
<td><input name="form_wifi_bssid" size="32" type="text" value="$(uci get credentials.wifi.bssid)" disabled></td>
</tr>

<tr><th></th><td></td></tr>
<tr><th>Access-Point-SSID:</th>
<TD class="nowrap"><INPUT NAME="form_wifi_ap_ssid_prefix" SIZE="16" TYPE="TEXT" VALUE="$(uci get ddmesh.system.community)" disabled>
<INPUT onchange="enable_custom_essid();" NAME="form_wifi_custom_essid" TYPE="CHECKBOX" VALUE="1"$(if [ "$(uci get ddmesh.network.custom_essid)" = "1" ];then echo ' checked="checked"';fi)>
<INPUT NAME="form_wifi_ap_ssid" SIZE="23" maxlength="15" TYPE="TEXT" VALUE="$(uci get ddmesh.network.essid_ap)"> aktuell: $(uci get wireless.@wifi-iface[1].ssid)</TD>
</tr>
<tr><th>Reduziere WLAN-Datenrate:</th><td><INPUT NAME="form_wifi_slow_rates" TYPE="CHECKBOX" VALUE="1"$(if [ "$(uci -q get ddmesh.network.wifi_slow_rates)" = "1" ];then echo ' checked="checked"';fi)> (Nicht empfohlen. Wenn aktiviert, kann Reichweite auf Kosten der &Uuml;bertragungsrate erh&ouml;ht werden. Dies gilt auch f&uuml;r Verbindungen zu anderen Knoten.)</td></tr>

<tr><td colspan="2"><hr size=1></td></tr>

<tr><th>Aktiviere privates WiFi:</th>
<td><INPUT onchange="enable_private_wifi();" id="id_wifi3_enabled" NAME="form_wifi3_enabled" TYPE="CHECKBOX" VALUE="1"$(if [ "$(uci -q get ddmesh.network.wifi3_enabled)" = "1" ];then echo ' checked="checked"';fi)>Erlaubt es, ein zusätzliches privates WiFi zu aktivieren.</td></tr>
<tr><th>Verschl&uuml;sselung deaktivieren:</th>
<td><INPUT id="id_wifi3_security_open" NAME="form_wifi3_security_open" TYPE="CHECKBOX" VALUE="1"$(if [ "$(uci -q get ddmesh.network.wifi3_security_open)" = "1" ];then echo ' checked="checked"';fi)>Offenes privates WiFi (sonst WPA2-PSK-verschl&uuml;sselt).</td></tr>
<tr><th>SSID:</th>
<td><input id="id_wifi3_ssid" name="form_wifi3_ssid" size="32" type="text" value="$(uci get credentials.wifi.private_ssid)"></td>
</tr>
<tr><th>Key (mind. 8 Zeichen):</th>
<td><input onkeypress="return isWifiKey(event);" id="id_wifi3_key" name="form_wifi3_key" width="30" type="text"></td>
</tr>
<tr><th>Verbinde WiFi mit:</th><td class="nowrap">
<input name="form_wifi3_network" type="radio" value="lan" $checked_lan>LAN
<input name="form_wifi3_network" type="radio" value="wan" $checked_wan>WAN
</td></tr>
<tr><td colspan="2">&nbsp;</td></tr>
<tr>
<td colspan="2"><input name="form_wifi_submit" title="Die Einstellungen &uuml;bernehmen. Diese werden erst nach einem Neustart wirksam." type="submit" value="&Uuml;bernehmen">&nbsp;&nbsp;&nbsp;<input name="form_wifi_abort" title="Abbrechen und &Auml;nderungen verwerfen." type="submit" value="Abbrechen"></td>
</tr>
</table>
</fieldset>
</form>
<br>

<fieldset class="bubble">
<legend>Kanal-Info</legend>
<table>
<tr><th>Frequenz</th><th>Kanal</th><th>Maximale Sendeleistung</th></tr>
$(iw phy0 info | sed -n '/[      ]*\*[   ]*[0-9]* MHz/{s#[       *]\+\([0-9]\+\) MHz \[\([0-9]\+\)\] (\(.*\))#<tr><td>\1</td><td>\2</td><td>\3</td></tr>#;p}')
</table>
</fieldset>

<script type="text/javascript">
enable_custom_essid();
enable_private_wifi();
setWifi3_key();
</script>

EOM

else #query string

	if [ -n "$form_wifi_submit" ]; then
		if [ -n "$form_wifi_txpower" ]; then
			uci set ddmesh.network.wifi_txpower="$form_wifi_txpower"
			uci set ddmesh.network.wifi_diversity="$form_wifi_diversity"
			uci set ddmesh.network.wifi_rxantenna="$form_wifi_rxantenna"
			uci set ddmesh.network.wifi_txantenna="$form_wifi_txantenna"
			uci set ddmesh.network.essid_ap="$(uhttpd -d "$form_wifi_ap_ssid")"
			uci set ddmesh.network.custom_essid="$form_wifi_custom_essid"
			uci set ddmesh.network.wifi_slow_rates="$form_wifi_slow_rates"
			uci set ddmesh.network.wifi3_enabled="$form_wifi3_enabled"
			# avoid clearing values when disabled
			if [ "$form_wifi3_enabled" = 1 ]; then
				uci set ddmesh.network.wifi3_network="$form_wifi3_network"
				uci set ddmesh.network.wifi3_security_open="$form_wifi3_security_open"
				uci set credentials.wifi.private_ssid="$form_wifi3_ssid"
				key=$(uhttpd -d "$form_wifi3_key")
				uci set credentials.wifi.private_key="$key"
			fi
			uci set ddmesh.boot.boot_step=2
			uci_commit.sh
			notebox "Die ge&auml;nderten Einstellungen wurden &uuml;bernommen. Die Einstellungen sind erst beim n&auml;chsten <A HREF="reset.cgi">Neustart</A> aktiv."
		else #empty
			notebox "TX-Power falsch."
		fi #empty
	else #submit
		notebox "Es wurden keine Einstellungen ge&auml;ndert."

	fi #submit
fi #query string

. /usr/lib/www/page-post.sh ${0%/*}
