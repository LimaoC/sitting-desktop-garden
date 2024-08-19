#!/bin/bash


WARN="[\033[1;33mWARN\033[0m]"
INFO="[\033[1;32mINFO\033[0m]"
ERROR="[\033[1;31mERROR\033[0m]"

PATHFILE=$1
TEMPDIRPATH='package_temp'

[ -d $TEMPDIRPATH ]
TEMPDIRCHECK=$?

# Make temp dir if it doesn't exist
if [ $TEMPDIRCHECK == 1 ]; then
	mkdir $TEMPDIRPATH
else
	echo -e "$INFO Temp directory was pre-existing. I promise not to delete it."
fi

cleanup () {
	# Do not delete the temp dir if it was pre-existing
	echo -e "$INFO Cleaning up"
	if [ $TEMPDIRCHECK == 1 ]; then
		rm -r $TEMPDIRPATH
	fi
}

BUILDPATH="${TEMPDIRPATH}/build"
mkdir $BUILDPATH

echo -e "$INFO Copying Files"

while read path; do
	if [[ $path == \#* ]]; then
		true
	elif [ -d $path ]; then
	#path is a directory
		cp -r --parents $path $BUILDPATH 			
	elif [ -e $path ]; then
	#path is just a file
		cp --parents $path ${BUILDPATH}
	else
		echo -e "${WARN}: $path not found"
	fi
done <$PATHFILE

# Hashing directory line from https://stackoverflow.com/questions/545387/linux-compute-a-single-hash-for-a-given-folder-contents
HASH=$( find ${BUILDPATH} -type f -print0 | sort -z | xargs -0 sha1sum | sha1sum )
TARNAME="build-${HASH:0:8}.tar" # Truncate the hash for a nicer file names

# Create tarball
echo -e "$INFO Creating Tarball"
if ! tar cf $TARNAME -C $TEMPDIRPATH "./build"; then
	echo -e "$ERROR Tarball creation failed"
	cleanup
	exit 1
fi

SSHTARGET=$2
# Check if we can find target
if ! nc -z $SSHTARGET 22 2>/dev/null; then
	echo -e "$ERROR Host unreachable";
	cleanup
	exit 1
fi

echo -e "$INFO Copying Tarball - destination's password may be needed"
if ! scp -q $TARNAME $SSHTARGET:~/; then
       echo -e "$ERROR Copy unsuccessful"
       cleanup
       exit 1
fi

echo -e "$INFO Extracting Build - the password may be needed again"
if ! ssh $SSHTARGET "tar xf $TARNAME; rm $TARNAME"; then
	echo -e "$ERROR Remote extraction failed"
	cleanup
	exit 1
fi

echo -e "$INFO Deployed Successfully"
cleanup
exit 0
