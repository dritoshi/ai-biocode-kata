rule samtools_sort:
    input:
        "results/{sample}.bam"
    output:
        "results/{sample}.sorted.bam"
    container:
        "docker://quay.io/biocontainers/samtools:1.20--h50ea8bc_0"
    shell:
        "samtools sort -o {output} {input}"
