# -----------------------------------------------------------------------------#
#                                Data Download                                 #
# -----------------------------------------------------------------------------#

rule download_nucleotide:
    """"
    Download files using the NCBI eutitilies.
    """
    message: "Downloading {wildcards.reads_origin} sample {wildcards.sample}.{wildcards.ext}"

    output:
        file = results_dir + "/data/{reads_origin}/{sample}/{sample}.{ext}"

    wildcard_constraints:
        ext = "(fna|gbff|gff)",
	      reads_origin = "(reference|nucleotide)",

    resources:
        cpus = 1,

    params:
        url = lambda wildcards: "https://eutils.ncbi.nlm.nih.gov/entrez/eutils/efetch.fcgi?db=nucleotide&id={accession}&rettype={rettype}&retmode=txt&api_key={api_key}".format(
          accession = wildcards.sample,
          rettype   = "gb" if wildcards.ext == "gbff" else "fasta",
          api_key   = config["api_key"],

        )

    shell:
      """
      curl -o {output.file} -s '{params.url}'
      if [[ {wildcards.reads_origin} == "reference" ]]; then
        if [[ {wildcards.ext} == "fna" || {wildcards.ext} == "gff" ]]; then
          python {scripts_dir}/rename_headers.py --file {output.file};
        fi;
      fi;      
      """