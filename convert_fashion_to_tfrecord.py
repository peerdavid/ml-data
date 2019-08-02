""" Converts all -uibyte.gz fashion mnist files to tf records
"""

import argparse
import os
import sys
import tensorflow as tf
import numpy as np


FASHION_MNIST_SIZE = 28


def _load_fashion(path, split):
    import os
    import gzip
    import numpy as np

    split = "t10k" if split == "test" else split

    """Load MNIST data from `path`"""
    labels_path = os.path.join(path,
                               '%s-labels-idx1-ubyte.gz'
                               % split)
    images_path = os.path.join(path,
                               '%s-images-idx3-ubyte.gz'
                               % split)

    with gzip.open(labels_path, 'rb') as lbpath:
        labels = np.frombuffer(lbpath.read(), dtype=np.uint8,
                               offset=8)
        

    with gzip.open(images_path, 'rb') as imgpath:
        images = np.frombuffer(imgpath.read(), dtype=np.uint8,
                               offset=16).reshape(len(labels), 784)
           
    return images, labels


def _write_tfrecords(path, images, labels, split):
    writer = tf.python_io.TFRecordWriter(path + split + ".tfrecords")
    num_images = len(images)
    for i in range(num_images):
        
        print("Writing image %d" % i)
        img = images[i].astype(np.float32).tostring()
        lab = labels[i].astype(np.int64)

        example = tf.train.Example(features=tf.train.Features(feature={
            "label": tf.train.Feature(int64_list=tf.train.Int64List(value=[lab])),
            "image": tf.train.Feature(bytes_list=tf.train.BytesList(value=[img])),
            "width": tf.train.Feature(int64_list=tf.train.Int64List(value=[FASHION_MNIST_SIZE])),
            "height": tf.train.Feature(int64_list=tf.train.Int64List(value=[FASHION_MNIST_SIZE])),
            "depth": tf.train.Feature(int64_list=tf.train.Int64List(value=[1]))
        }))
        writer.write(example.SerializeToString())
    writer.close()


def convert_to_tf_record(path):
    input_path = path + "/ubyte/"
    output_path = path + "/tfrecord/"

    images, labels = _load_fashion(input_path, "train")
    _write_tfrecords(output_path, images, labels, "train")

    images, labels = _load_fashion(input_path, "test")
    _write_tfrecords(output_path, images, labels, "test")



if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    
    parser.add_argument(
        '--data-directory', 
        default='./data/fashionMNIST',
        help='Directory where TFRecords will be stored')

    args = parser.parse_args()
    convert_to_tf_record(os.path.expanduser(args.data_directory))