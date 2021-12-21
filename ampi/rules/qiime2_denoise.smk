rule qiime2_denoise_dada2:
    input:
        os.path.join(config["output"]["import"], "demux.qza")
    output:
        rep_seq = os.path.join(config["output"]["denoise"], "dada2/rep_seqs.qza"),
        table = os.path.join(config["output"]["denoise"], "dada2/table.qza"),
        stats = os.path.join(config["output"]["denoise"], "dada2/denoise_stats.qza")
    params:
        trunc_len_f = config["params"]["denoise"]["dada2"]["trunc_len_f"],
        trunc_len_r = config["params"]["denoise"]["dada2"]["trunc_len_r"],
        trim_left_f = config["params"]["denoise"]["dada2"]["trim_left_f"],
        trim_left_r = config["params"]["denoise"]["dada2"]["trim_left_r"]
    log:
        os.path.join(config["output"]["denoise"], "logs/denoise_dada2.log")
    threads:
        config["params"]["denoise"]["threads"]
    shell:
        '''
        qiime dada2 denoise-paired \
        --i-demultiplexed-seqs {input} \
        --p-trunc-len-f {params.trunc_len_f} \
        --p-trunc-len-r {params.trunc_len_r} \
        --p-trim-left-f {params.trim_left_f} \
        --p-trim-left-r {params.trim_left_r} \
        --o-representative-sequences {output.rep_seq} \
        --o-table {output.table} \
        --o-denoising-stats {output.stats} \
        --verbose \
        --p-n-threads {threads} > {log} 2>&1
        '''


rule qiime2_denoise_deblur:
    input:
        os.path.join(config["output"]["import"], "demux.qza")
    output:
        demux = os.path.join(config["output"]["denoise"], "deblur/demux_filtered.qza"),
        demux_stats = os.path.join(config["output"]["denoise"], "deblur/demux_filtered_stats.qza"),
        rep_seq = os.path.join(config["output"]["denoise"], "deblur/rep_seqs.qza"),
        table = os.path.join(config["output"]["denoise"], "deblur/table.qza"),
        stats = os.path.join(config["output"]["denoise"], "deblur/denoise_stats.qza")
    params:
        trim_len = config["params"]["denoise"]["deblur"]["trim_len"],
        left_trim_len = config["params"]["denoise"]["deblur"]["left_trim_len"]
    log:
        os.path.join(config["output"]["denoise"], "logs/denoise_deblur.log")
    threads:
        config["params"]["denoise"]["threads"]
    shell:
        '''
        qiime quality-filter q-score \
        --i-demux {input} \
        --o-filtered-sequences {output.demux} \
        --o-filter-stats {output.demux_stats} > {log} 2>&1

        qiime deblur denoise-16S \
        --i-demultiplexed-seqs {output.demux} \
        --p-trim-length {params.trim_len} \
        --p-left-trim-length {params.left_trim_len} \
        --p-sample-stats \
        --o-representative-sequences {output.rep_seq} \
        --o-table {output.tab} \
        --o-stats {output.stats} >> {log} 2>& 1
        '''
