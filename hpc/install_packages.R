# Run once on the cluster (login node or a short job): installs the R packages the pipeline uses.
# Versions used in development: AlphaSimR 2.1.0, sommer 4.5.12, BGLR 1.1.4, rrBLUP 4.6.3, nadiv 2.18.0.
lib <- Sys.getenv("R_LIBS_USER"); dir.create(lib, recursive = TRUE, showWarnings = FALSE)
pk <- c("AlphaSimR", "data.table", "Matrix", "nadiv", "sommer", "rrBLUP", "BGLR", "ggplot2",
        "knitr", "rmarkdown", "quadprog")
need <- setdiff(pk, rownames(installed.packages()))
if (length(need)) install.packages(need, lib = lib, repos = "https://cloud.r-project.org")
print(sapply(pk, function(p) as.character(packageVersion(p))))
if (!rmarkdown::pandoc_available()) cat("WARNING: pandoc not found - load a pandoc module or install it; rmarkdown needs it for html output\n")
