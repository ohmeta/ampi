#!/usr/bin/env python

import argparse
import os
import gzip
from Bio import SeqIO, bgzf
import pandas as pd
import time


def parse_samples(run_tsv, out_dir, do_demultiplex=False):
    # run reads barcode
    samples_df = pd.read_csv(run_tsv, sep='\s+')
    if do_demultiplex:
        samples_df = samples_df\
            .assign(id=samples_df.apply(lambda x: str(x.run) + "_" + str(x.barcode_id)),
                    fq=samples_df.apply(lambda x: os.path.join(out_dir, str(x.id) + ".fq.gz")))
    import pprint
    pprint.pprint(samples_df)
    return samples_df


def get_run_fq(sample_df, wildcards, col):
    return sample_df.loc[[wildcards.run], col].dropna().tolist()[0]


def demultiplexer(reads_file, barcode_file, sample_barcode, prefix, trunk_size=1000000):
    if reads_file.endswith(".gz"):
        reads_h = gzip.open(reads_file, 'rt')
    else:
        reads_h = open(reads_file, 'r')
    if barcode_file.endswith(".gz"):
        barcode_h = gzip.open(barcode_file, 'rt')
    else:
        barcode_h = open(barcode_file, 'r')

    reads_partition = {}
    out_partition = {}
    for barcode_seq in sample_barcode.index:
        reads_partition[barcode_seq] = []
        out_partition[barcode_seq] = bgzf.BgzfWriter(sample_barcode.loc[barcode_seq, "fq"], 'wb')
    reads_partition["undetermined"] = []
    out_partition["undetermined"] = bgzf.BgzfWriter(prefix + "_undetermined" + ".fq.gz", 'wb')
    count = 0

    for read, barcode in zip(SeqIO.parse(reads_h, 'fastq'), SeqIO.parse(barcode_h, 'fastq')):
        count += 1
        if str(barcode.seq) in reads_partition:
            reads_partition[str(barcode.seq)].append(read)
        else:
            reads_partition["undetermined"].append(read)

        if count == trunk_size:
            for barcode_seq in reads_partition:
                if len(reads_partition[barcode_seq]) > 0:
                    SeqIO.write(reads_partition[barcode_seq], out_partition[barcode_seq], 'fastq')
                    reads_partition[barcode_seq] = []
            count = 0

    for barcode_seq in reads_partition:
        if len(reads_partition[barcode_seq]) > 0:
            SeqIO.write(reads_partition[barcode_seq], out_partition[barcode_seq], 'fastq')
            reads_partition[barcode_seq] = []
        out_partition[barcode_seq].close()


def main():
    parser = argparse.ArgumentParser("split fastq file by sample barcode")
    parser.add_argument('-r', '--reads', type=str, help='fastq file')
    parser.add_argument('-b', '--barcode', type=str, help='barcode file')
    parser.add_argument('-s', '--samples', type=str, help='samples and barcode information')
    parser.add_argument('-p', '--prefix', type=str, help='output prefix')

    args = parser.parse_args()
    os.makedirs(os.path.dirname(args.prefix), exist_ok=True)
    start_time = time.time()

    sample_barcode = pd.read_csv(args.samples, sep='\t').set_index('barcode', drop=False)
    sample_barcode = sample_barcode.assign(fq=sample_barcode.barcode_id.apply(
        lambda x: args.prefix + "_" + str(x) + ".fq.gz"))

    demultiplexer(args.reads, args.barcode, sample_barcode, args.prefix)
    print("demultiplex %d samples form %s has spent %s s" % (len(sample_barcode), args.reads, time.time() - start_time))


if __name__ == '__main__':
    main()
