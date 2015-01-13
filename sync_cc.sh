#!/bin/bash
#
# This script is used to keep the cluster nodes in sync on the config side
# The script can be executed on either of the nodes!  
# Take care to not do anything in here that can only be done on the active node!!!
#

##### Variables #####
# Cluster hosts
HOST1=<host name 1>
IP1=<host IP 1>
HOST2=<host name 2>
IP2=<host IP 2>

# Color settings for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\e[0;33m'
NC='\033[0m' # No Color

# rsync params
RSYNCPARAMS="-av"

echo -e "\n${YELLOW}Cluster config synchronisation started...${NC}"

##### Pre checks #####
# We need to run as root here
if [[ $EUID -ne 0 ]]; then
   echo -e "${RED}This script must be run as root!${NC}" 1>&2
   exit 1
fi

# Check on which node we run
CURRENT=`cat /etc/hostname`
if [[ ${CURRENT} = ${HOST1} || ${CURRENT} = ${HOST2} ]]; then
    if [[ ${CURRENT} = ${HOST1} ]]; then
        OTHER=$IP2
	OTHER_HOST=$HOST2
    else
        OTHER=$IP1
	OTHER_HOST=$HOST1
    fi
    echo -e "Running on cluster member node ${GREEN}${CURRENT}${NC}, syncing with node ${GREEN}${OTHER_HOST}${NC}"
else
    echo -e "${RED}Node is not a cluster member!${NC}" 1>&2
    exit 1
fi

# Echo sync time to sync dir
INFO_FILE='/srv/http/sync.info'
echo "Last sync was executed form ${CURRENT} to ${OTHER_HOST}" > $INFO_FILE
date >> $INFO_FILE


##### Sync code #####

# sync content of sync folder in home
echo -e "\nSyncing home sync stuff..."
rsync ${RSYNCPARAMS} /home/labuser/sync ${OTHER}:/home/labuser/

# sync the ha config
echo -e "\nSyncing ha config..."
rsync ${RSYNCPARAMS} /etc/ha.d ${OTHER}:/etc/

# sync the drbd config
echo -e "\nSyncing drbd config..."
rsync ${RSYNCPARAMS} /etc/drbd.d ${OTHER}:/etc/

# sync the samba config
echo -e "\nSyncing samba config..."
rsync ${RSYNCPARAMS} /etc/samba ${OTHER}:/etc/

# sync the lighttp config
echo -e "\nSyncing lighttpd config..."
rsync ${RSYNCPARAMS} /etc/lighttpd ${OTHER}:/etc/

# sync the ssmtp config
echo -e "\nSyncing ssmtp config..."
rsync ${RSYNCPARAMS} /etc/ssmtp ${OTHER}:/etc/

# sync the content of the httpd
echo -e "\nSyncing httpd content..."
rsync ${RSYNCPARAMS} /srv/http/ $OTHER:/srv/http/

# sync config files
echo -e "\nSyncing other config files in /etc..."
# files/directories under '/etc' to be synched
FILES="rsyncd.conf rsyncd.scrt exports idmapd.conf named.conf rndc.key dhcpd.conf dhcpd-static-*.conf ntp.conf"
INCLUDES=""
for file_name in ${FILES}; do INCLUDES="${INCLUDES} --include=${file_name}"; done
rsync ${RSYNCPARAMS} ${INCLUDES} --exclude='*' /etc/ ${OTHER}:/etc/

##### end #####

echo -e "\n${GREEN}Finished${NC}\n"
