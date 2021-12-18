# ncov phylogeography

## Install

1. Download git repository.

    ```bash
    git clone https://github.com/ktmeaton/ncov-phylogeography.git
    cd ncov-phylogeography
    ```

1. Create conda environment

    ```
    mamba env create -f workflow/envs/main/environment.yaml
    conda activate ncov-phylogeography
    ```

1. Run snakemake pipeline.

    ```bash
    snakemake --profile workflow/profiles/laptop all
    ```

1. Visualize.

    ```bash
    auspice view --datasetDir results/auspice/nucleotide/
    ```