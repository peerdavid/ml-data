#!/bin/bash


#
# smallNORB
#
DATADIR="./data/smallNORB/mat"
mkdir -p "./data/smallNORB/tfrecord"
mkdir -p $DATADIR

while read url ; do
    echo "fetching $url"
    wget -P "$DATADIR/" "$url"
done < "./url_norb.txt"

echo "smallNORB: Done fetching archive files. Extracting..."

for gzfile in $DATADIR/*.gz ; do
   gzip -d "$gzfile"
done


#
# MNIST
#
mkdir -p "./data/mnist/tfrecord"
mkdir -p "./data/mnist/ubyte"


#
# Fashion MNIST
#
DATADIR="./data/fashionMNIST/ubyte"
mkdir -p $DATADIR
mkdir -p "./data/fashionMNIST/tfrecord"

while read url ; do
    echo "fetching $url"
    wget -P "$DATADIR/" "$url"
done < "./url_fashion.txt"

echo "fashionMNIST: Done fetching archive files. Extracting..."

echo "Done!"
