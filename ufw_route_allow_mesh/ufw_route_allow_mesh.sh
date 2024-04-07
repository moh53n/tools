#!/bin/bash

# Interface names (Replace with yours)
interfaces=(eth0 eth1 eth2 eth3)

for A in "${interfaces[@]}"
do
    for B in "${interfaces[@]}"
    do
        if [ "$A" != "$B" ]; then
            sudo ufw route allow in on "$A" out on "$B"  # ufw will skip duplicate rules, so it's safe to just add new interfaces and run again
        fi
    done
done