#!/bin/bash
#4chan image scraping utility

main () {
# -P specifies directory
# -nd prevents directory creation
# -r recursive download
# -l level of recursion
# -H go to foreign hosts when recursive
# -D specify domains
# $@ all args when called
wget -P ~/Pictures -nd -r -l 1 -H -D is2.4chan.org -A png,gif,jpg,jpeg,webm -R '*s.*' $@
}

loopy=false

while getopts f::hv arg; do
  case $arg in
    f) loopy=true && filepath="${OPTARG}" && echo "${OPTARG} test $filepath"  
    ;;
    h) printf "Help:\n-----\n\nFormat\n4chan-image-scrape.sh [OPTIONS] <Web Link or File>\n-h: Help Page\n-v Version Information\n-f File to read from\n" ; exit
    ;;
    v) printf "Version 0.2\n" ; exit
    ;;
    *) printf "Help:\n-----\n\nFormat\n4chan-image-scrape.sh [OPTIONS] <Web Link or File>\n-h: Help Page\n-v Version Information\n-f File to read from\n" ; exit
  esac
done  

$loopy || main "${@: -1}"
$loopy && while read i; do main "$i"; done <$filepath 
