#!/usr/bin/env cwl-runner
cwlVersion: v1.2
class: Workflow
label: minimal paired-end RNA-seq workflow

inputs:
  fastq_r1: File
  fastq_r2: File
  sample_name: string
  genome_index: Directory

outputs:
  bam:
    type: File
    outputSource: align/bam_output
  fastp_report:
    type: File
    outputSource: filter/report_html

steps:
  filter:
    run: fastp_filter.cwl
    in:
      fastq_r1: fastq_r1
      fastq_r2: fastq_r2
      sample_name: sample_name
    out: [filtered_r1, filtered_r2, report_html]

  align:
    run: hisat2_align.cwl
    in:
      fastq_r1: filter/filtered_r1
      fastq_r2: filter/filtered_r2
      genome_index: genome_index
      sample_name: sample_name
    out: [bam_output]
