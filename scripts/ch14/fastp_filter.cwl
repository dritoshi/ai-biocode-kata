#!/usr/bin/env cwl-runner
cwlVersion: v1.2
class: CommandLineTool
label: paired-end FASTQ filtering with fastp
baseCommand: fastp

requirements:
  InlineJavascriptRequirement: {}

hints:
  DockerRequirement:
    dockerPull: quay.io/biocontainers/fastp:0.23.4--h125f33a_5

inputs:
  fastq_r1:
    type: File
    inputBinding:
      prefix: --in1
  fastq_r2:
    type: File
    inputBinding:
      prefix: --in2
  sample_name:
    type: string

arguments:
  - prefix: --out1
    valueFrom: $(inputs.sample_name)_filtered_R1.fastq.gz
  - prefix: --out2
    valueFrom: $(inputs.sample_name)_filtered_R2.fastq.gz
  - prefix: --html
    valueFrom: $(inputs.sample_name)_fastp.html

outputs:
  filtered_r1:
    type: File
    outputBinding:
      glob: $(inputs.sample_name)_filtered_R1.fastq.gz
  filtered_r2:
    type: File
    outputBinding:
      glob: $(inputs.sample_name)_filtered_R2.fastq.gz
  report_html:
    type: File
    outputBinding:
      glob: $(inputs.sample_name)_fastp.html
