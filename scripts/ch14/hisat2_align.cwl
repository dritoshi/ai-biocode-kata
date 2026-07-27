#!/usr/bin/env cwl-runner
cwlVersion: v1.2
class: CommandLineTool
label: paired-end alignment with HISAT2 and SAMtools
baseCommand: bash

requirements:
  InlineJavascriptRequirement: {}

inputs:
  fastq_r1: File
  fastq_r2: File
  genome_index: Directory
  sample_name: string

arguments:
  - -c
  - valueFrom: |
      set -euo pipefail
      hisat2 \
        -x "$(inputs.genome_index.path)/genome" \
        -1 "$(inputs.fastq_r1.path)" \
        -2 "$(inputs.fastq_r2.path)" \
        2> "$(inputs.sample_name)_hisat2.log" \
        | samtools view -b -o "$(inputs.sample_name).bam" -

outputs:
  bam_output:
    type: File
    outputBinding:
      glob: $(inputs.sample_name).bam
