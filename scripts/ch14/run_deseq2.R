# 最小カウント行列からDESeq2の解析結果をCSVへ保存する

run_deseq2 <- function(counts_path, samples_path, output_path, log_path) {
    suppressPackageStartupMessages(library(DESeq2))

    dir.create(dirname(output_path), recursive = TRUE, showWarnings = FALSE)
    dir.create(dirname(log_path), recursive = TRUE, showWarnings = FALSE)

    log_connection <- file(log_path, open = "wt")
    sink(log_connection, type = "output")
    sink(log_connection, type = "message")
    on.exit({
        sink(type = "message")
        sink(type = "output")
        close(log_connection)
    }, add = TRUE)

    message("カウント行列とサンプル情報を読み込む")
    count_table <- read.delim(
        counts_path,
        row.names = 1,
        check.names = FALSE
    )
    sample_table <- read.delim(
        samples_path,
        row.names = 1,
        check.names = FALSE
    )

    if (!identical(colnames(count_table), rownames(sample_table))) {
        stop("カウント行列の列順とサンプル情報の行順が一致しない")
    }
    if (!all(c("control", "treated") %in% sample_table$condition)) {
        stop("condition列にはcontrol群とtreated群の両方が必要である")
    }

    count_matrix <- as.matrix(count_table)
    storage.mode(count_matrix) <- "integer"
    sample_table$condition <- factor(
        sample_table$condition,
        levels = c("control", "treated")
    )

    dds <- DESeqDataSetFromMatrix(
        countData = count_matrix,
        colData = sample_table,
        design = ~condition
    )
    dds <- DESeq(dds, fitType = "mean", quiet = TRUE)
    result <- results(
        dds,
        contrast = c("condition", "treated", "control")
    )
    result_table <- data.frame(
        gene_id = rownames(result),
        as.data.frame(result),
        check.names = FALSE
    )
    write.csv(result_table, output_path, row.names = FALSE)
    message(sprintf("%d遺伝子の結果を保存した", nrow(result_table)))
}

if (exists("snakemake")) {
    run_deseq2(
        snakemake@input[["counts"]],
        snakemake@input[["samples"]],
        snakemake@output[["results"]],
        snakemake@log[[1]]
    )
} else {
    args <- commandArgs(trailingOnly = TRUE)
    if (length(args) != 4) {
        stop(
            paste(
                "使い方: Rscript run_deseq2.R",
                "counts.tsv samples.tsv results.csv run.log"
            )
        )
    }
    run_deseq2(args[[1]], args[[2]], args[[3]], args[[4]])
}
