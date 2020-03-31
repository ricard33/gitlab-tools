#!/bin/bash
# Author: Cedric RICARD
echo "CHANGELOG"
echo ----------------------
PATH="/c/Git/bin:$PATH"
# GIT_OPTIONS="--no-merges --date=short"
GIT_OPTIONS="--date=short"
#git tag -l "[0-9]*.[0-9]*.[0-9]*" | sort -u -r -n -t. -k1,1 -k2,2 -k3,3 -k4,4 | while read TAG ; do
git tag -l | grep "v\?[0-9]\+\.[0-9]\+" | sort -u -r -n -t. -k1,1 -k2,2 -k3,3 -k4,4 | while read TAG ; do
#git for-each-ref --sort='-*authordate' --format='%(tag)' refs/tags/[0-9]*.[0-9]*.[0-9]* | while read TAG ; do
    echo
    if [ $NEXT ];then
		DATE=$(git log -1 --format=%ad --date=short $NEXT)
        echo "[$NEXT] $DATE"
		echo "-----------------------"
		echo
		echo "### changes ###"
		echo
    else
        echo "[Current]"
    fi
    GIT_PAGER=cat git log $GIT_OPTIONS --format=' * %ad %s' $TAG..$NEXT
    NEXT=$TAG
done
#FIRST=$(git for-each-ref --sort='*authordate' --format='%(tag)' refs/tags/[0-9]*.[0-9]*.[0-9]* | head -1)
FIRST=$(git tag -l "[0-9]*.[0-9]*.[0-9]*" | sort -u | head -1)
DATE=$(git log -1 --format=%ad --date=short $FIRST)

echo
echo [$FIRST] $DATE
echo "-------------------"
echo
GIT_PAGER=cat git log $GIT_OPTIONS --format=' * %ad %s' $FIRST
