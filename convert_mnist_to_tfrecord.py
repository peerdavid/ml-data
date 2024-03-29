
#! /usr/env/bin python3

"""Convert MNIST Dataset to local TFRecords"""

import argparse
import os
import sys
import numpy as np
from urllib import request
import gzip
import pickle
import tensorflow as tf
from tensorflow.examples.tutorials.mnist import input_data


UBYTE_PATH = "data/mnist/ubyte/"

# Credit for downloading and loading ubyte files - https://github.com/hsjeong5/
filename = [
    ["training_images","train-images-idx3-ubyte.gz"],
    ["test_images","t10k-images-idx3-ubyte.gz"],
    ["training_labels","train-labels-idx1-ubyte.gz"],
    ["test_labels","t10k-labels-idx1-ubyte.gz"]]


def download_mnist():
    base_url = "http://yann.lecun.com/exdb/mnist/"
    for name in filename:
        print("Downloading "+name[1]+"...")
        request.urlretrieve(base_url + name[1], UBYTE_PATH + name[1])
    print("Download complete.")


def load_mnist():
    mnist = {}
    for name in filename[:2]:
        with gzip.open(UBYTE_PATH + name[1], 'rb') as f:
            mnist[name[0]] = np.frombuffer(f.read(), np.uint8, offset=16).reshape(-1,28*28).astype(np.float32)
    for name in filename[-2:]:
        with gzip.open(UBYTE_PATH + name[1], 'rb') as f:
            mnist[name[0]] = np.frombuffer(f.read(), np.uint8, offset=8).astype(np.float32)
    return mnist


def _data_path(data_directory:str, name:str) -> str:
    """Construct a full path to a TFRecord file to be stored in the 
    data_directory. Will also ensure the data directory exists
    
    Args:
        data_directory: The directory where the records will be stored
        name:           The name of the TFRecord
    
    Returns:
        The full path to the TFRecord file
    """
    if not os.path.isdir(data_directory):
        os.makedirs(data_directory)

    return os.path.join(data_directory, f'{name}.tfrecords')

def _int64_feature(value:int) -> tf.train.Features.FeatureEntry:
    """Create a Int64List Feature
    
    Args:
        value: The value to store in the feature
    
    Returns:
        The FeatureEntry
    """
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

def _bytes_feature(value:str) -> tf.train.Features.FeatureEntry:
    """Create a BytesList Feature
    
    Args:
        value: The value to store in the feature
    
    Returns:
        The FeatureEntry
    """
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def convert_to(images, labels, name:str, data_directory:str, num_shards:int=1):
    """Convert the dataset into TFRecords on disk
    
    Args:
        data_set:       The MNIST data set to convert
        name:           The name of the data set
        data_directory: The directory where records will be stored
        num_shards:     The number of files on disk to separate records into
    """
    print(f'Processing {name} data')
   
    num_examples = len(images)
    depth = 1
    width = 28
    height = 28

    def _process_examples(start_idx:int, end_index:int, filename:str):
        with tf.python_io.TFRecordWriter(filename) as writer:
            for index in range(start_idx, end_index):
                sys.stdout.write(f"\rProcessing sample {index+1} of {num_examples}")
                sys.stdout.flush()

                image_raw = images[index].tostring()
                example = tf.train.Example(features=tf.train.Features(feature={
                    'height': _int64_feature(height),
                    'width': _int64_feature(width),
                    'depth': _int64_feature(depth),
                    'label': _int64_feature(int(labels[index])),
                    'image_raw': _bytes_feature(image_raw)
                }))
                writer.write(example.SerializeToString())
    
    if num_shards == 1:
        _process_examples(0, num_examples, _data_path(data_directory, name))
    else:
        total_examples = num_examples
        samples_per_shard = total_examples // num_shards

        for shard in range(num_shards):
            start_index = shard * samples_per_shard
            end_index = start_index + samples_per_shard
            _process_examples(start_index, end_index, _data_path(data_directory, f'{name}-{shard+1}'))

    print()


def convert_to_tf_record(data_directory:str):
    """Convert the TF MNIST Dataset to TFRecord formats
    
    Args:
        data_directory: The directory where the TFRecord files should be stored
    """

    download_mnist()
    mnist = load_mnist()
    
    convert_to(mnist["training_images"], mnist["training_labels"], 'train', data_directory)
    convert_to(mnist["test_images"], mnist["test_labels"], 'test', data_directory)


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        '--data-directory', 
        default='./data/mnist/tfrecord',
        help='Directory where TFRecords will be stored')

    args = parser.parse_args()
    convert_to_tf_record(os.path.expanduser(args.data_directory))