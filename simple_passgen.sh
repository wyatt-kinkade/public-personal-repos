#!/bin/bash
 
echo "How many characters should the password have?"

read passwordlength

</dev/urandom tr -dc 'A-Za-z0-9!"#$%&' | head -c $passwordlength ; echo
