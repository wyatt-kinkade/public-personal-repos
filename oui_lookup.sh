read -p "MAC Address or OUI to search: " MAC_VAL

#Ripping out common delimiters and then only using the first 6 characters of the string
REFINED_MAC=`echo "$MAC_VAL" | tr -d '.' | tr -d '-' | tr -d ':' | head -c 6`

#Dodging awk to speed things up
curl -sS "http://standards-oui.ieee.org/oui/oui.txt" | grep -i "$REFINED_MAC" | cut -d')' -f2 | tr -d '\t'

