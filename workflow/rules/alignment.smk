include: "functions.smk"

# -----------------------------------------------------------------------------#
#                               Genome Alignments                              #
# -----------------------------------------------------------------------------#

# -----------------------------------------------------------------------------#
rule snippy_pairwise:
  """
  Peform a pairwise alignment of assemblies to the reference genome.
  """
  message: "Aligning {wildcards.reads_origin} sample {wildcards.sample} to the reference."

  input:
    data = results_dir + "/data/{reads_origin}/{sample}/{sample}.fna",
    ref  = results_dir + "/data/reference/{sample}/{sample}.fna".format(
            sample=config["reference_accession"],
           )

  output:
    snippy_dir = directory(results_dir + "/snippy_pairwise/{reads_origin}/{sample}/"),
    snps_tab   =           results_dir + "/snippy_pairwise/{reads_origin}/{sample}/{sample}.tab",
    snp_txt    =           results_dir + "/snippy_pairwise/{reads_origin}/{sample}/{sample}.txt",
    snippy_aln =           results_dir + "/snippy_pairwise/{reads_origin}/{sample}/{sample}.aligned.fa",
    snps_vcf   =           results_dir + "/snippy_pairwise/{reads_origin}/{sample}/{sample}.subs.vcf",
    raw_vcf    =           results_dir + "/snippy_pairwise/{reads_origin}/{sample}/{sample}.raw.vcf",
    log        =           results_dir + "/snippy_pairwise/{reads_origin}/{sample}/{sample}.log",  

  resources:
    load=100,
    time_min=600,
    cpus=workflow.global_resources["cpus"] if ("cpus" in workflow.global_resources) else 1,
    mem_mb=workflow.global_resources["mem_mb"] if ("mem_mb" in workflow.global_resources) else 4000,

  wildcard_constraints:
    reads_origin="(local|nucleotide)", 
    
  shell:
    """
    snippy \
      --prefix {wildcards.sample} \
      --reference {input.ref} \
      --outdir {output.snippy_dir} \
      --ctgs {input.data} \
      --mapqual {config[map_qual]} \
      --mincov {config[min_depth]} \
      --minfrac {config[min_frac]} \
      --basequal {config[base_qual]} \
      --force \
      --cpus {resources.cpus} \
      --report; 
    """

# -----------------------------------------------------------------------------#

rule snippy_multi:
  """
  Peform a multiple alignment from pairwise output.
  """
  input:
    snippy_pairwise_dir = [
                          results_dir + "/snippy_pairwise/{reads_origin}/" + "{accession}/".format(
                            accession=accession,
                          )
                          for accession in identify_nucleotide_samples()
                          ],
    ref                 = results_dir + "/data/reference/{sample}/{sample}.fna".format(
                          sample=config["reference_accession"],
                          )    
  output:
    full_aln            = results_dir + "/snippy_multi/{reads_origin}/snippy-multi.full.aln", 
    log                 = results_dir + "/snippy_multi/{reads_origin}/snippy-multi.log",

  shell:
    """
    set +e;
    snippy-core \
      --ref {input.ref} \
      --prefix {results_dir}/snippy_multi/{wildcards.reads_origin}/snippy-multi \
      --mask auto \
      --mask-char {config[mask_char]} \
      {input.snippy_pairwise_dir};
    exitcode=$?;
    if [ $exitcode -eq 1 ]
    then
        exit 1
    else
        exit 0
    fi      
    """