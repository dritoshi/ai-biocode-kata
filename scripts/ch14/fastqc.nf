// 単一または複数のFASTQからFastQCレポートを生成するDSL2ワークフロー

nextflow.enable.dsl = 2

params.reads = "data/raw/*.fastq.gz"
params.outdir = "results"

process FASTQC {
    tag "${sample_id}"
    publishDir "${params.outdir}/qc", mode: "copy"

    input:
    tuple val(sample_id), path(fastq)

    output:
    tuple val(sample_id),
        path("${sample_id}_fastqc.html"),
        path("${sample_id}_fastqc.zip"),
        emit: reports

    script:
    """
    fastqc "${fastq}" --outdir .
    """
}

workflow {
    reads_ch = Channel
        .fromPath(params.reads, checkIfExists: true)
        .map { fastq -> tuple(fastq.simpleName, fastq) }

    FASTQC(reads_ch)
}
