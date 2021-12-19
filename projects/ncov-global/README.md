# SARS-CoV-2 Global

## Data

- 5000 samples for visualization
- Ancestral reconstructions:
    - Country
    - Pangolin Lineage

- Each `snippy_pairwise` folder is 2MB:
    - 500 samples : 1 GB
    - 1000 samples : 2 GB
    - 5000 samples : 10 GB
    - ...
    - 2 million samples : 4 TB

- Subsampling hierarchy:
    - Pangolin Lineage
        - Country
            - Date

- I can't pairwise align 2 million samples. 
- For global data, do I use NCBI or GISAID?
- For NCBI, I can't know the pangolin lineage in advance.
- All | `("sars-cov-2[organism]) AND (29000[SLEN] : 30000[SLEN])` | 2,721,897 records
- 1 month | `sars-cov-2[organism] AND (29000[SLEN] : 30000[SLEN]) AND (2021/11/19[PDAT] : 2021/12/31[PDAT]))` | 389,791 records
- 1 week | `sars-cov-2[organism] AND (29000[SLEN] : 30000[SLEN]) AND (2021/12/12[PDAT] : 2021/12/19[PDAT]))` | 34,670

- This is an optimization problem.
- We want to maximize genetic diversity and geographic locations.
- We want to minimize identical samples collected from the same location. 

- Metadata collection bottleneck:
    - NCBI API max 10 records / second
    - 100,000 records = 2.7 hours
    - 500,000 records = 5.4 hours
    - 1,000,000 records = 27 hours

- Can I use GISAID metadata to inform sample selection?
- I don't think NCBI is going to work, Canadian sequences are not on there.

### CoVizu

#### Filtering

1. Lacks a Pango lineage assignment.
2. Was sampled from a non-human host.
3. Was shorter than 29,000 nt.
4. Lacks a complete sample collection date (e.g., year and month with no day.
5. Was labeled with a collection date preceding 1 December 2019 or in the future.

#### Down-Sampling

1. Sequences from the last 24 hours are bulk downloaded from the GISAID database. All developers have signed the GISAID data access agreement, and sequences are not being re-distributed.

2. Sequences are aligned pairwise against the SARS-COV-2 reference genome using the short read mapper minimap2 and a Python wrapper minimap2.py that applies the CIGAR string to each genome to either reconstitute the aligned sequence or extract all differences from the reference.

3. Genomes are classified into Pangolin lineages using the script pangolearn.py.

4. A single representative genome is selected for each Pangolin lineage. We take the most recent sample that pass all of our filtering criteria (<1% uncalled bases, genetic divergence consistent with molecular clock, with all problematic sites filtered out).

5. A time-scaled tree is reconstructed using a combination of fasttree2 and TreeTime.

6. For all genomes within each lineage, we extract all genetic differences from the reference genome as "features", which provides a highly compact representation of that genome. We calculate the symmetric difference of each genome to every other genome and cache the result on the filesystem.

7. For each lineage, we generate 100 replicate bootstrap samples of the feature set union to convert the symmetric differences into distance matrices, treating every genetic difference equally (Manhattan distance). Each distance matrix is used to reconstruct a neighbor-joining tree using RapidNJ.

8. For each lineage, a consensus tree is calculated from the set of bootstrap trees and converted into a beadplot.


## Questions

1. Frequencies of circulating lineages (ex. [H3N2](https://nextstrain.org/flu/seasonal/h3n2/ha/2y)).
1. Importers vs. Exporters ([Migrations](https://www.eurosurveillance.org/content/10.2807/1560-7917.ES.2021.26.44.2001996#figuresntables)).
1. Number of introductions.
1. Number of community transmissions.
1. Variant origins (time, location).

## Lineages

Pangolin lineages are here:
    - https://github.com/cov-lineages/pango-designation/raw/master/lineage_notes.txt

`wget -q -O - https://github.com/cov-lineages/pango-designation/raw/master/lineage_notes.txt | grep -v "Withdrawn" > pango_lineages.txt`