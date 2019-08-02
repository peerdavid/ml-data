#!/bin/bash

./download.sh
python3 convert_fashion_to_tfrecord.py
python3 convert_mnist_to_tfrecord.py
python3 convert_norb_to_tfrecord.py