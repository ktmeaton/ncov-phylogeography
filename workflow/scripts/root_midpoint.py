#!/usr/bin/env python3

import os
from Bio import Phylo
import click

# -------------------------------------------------------------------------
# Command Line Arguments
# -------------------------------------------------------------------------

@click.command()
@click.help_option("--help", "-h")

# -------------------------------------------------------------------------
# Mandatory

@click.option(
    "-t",
    "--tree",
    help="Input newick tree.",
    type=click.Path(exists=True, dir_okay=False, allow_dash=True),
    required=True,
)
@click.option(
    "-o",
    "--outdir",
    help="Output directory.",
    type=click.Path(dir_okay=True, allow_dash=True),
    required=False,
    default=os.getcwd(),
)
def main(
    tree: str, outdir: str,
):
    """This script roots a newick tree at the midpoint."""

    tree_path = tree
    out_dir = outdir
    tree_basename = os.path.splitext(os.path.basename(tree_path))[0]

    # -------------------------------------------------------------------------
    # Import Tree
    tree = Phylo.read(tree_path, "newick")
    tree.ladderize(reverse=False)

    tree.root_at_midpoint()
    tree.ladderize(reverse=False)
    
    Phylo.draw_ascii(tree)
    out_path = os.path.join(out_dir, tree_basename + ".nwk")
    Phylo.write(tree, out_path, format="newick")

if __name__ == "__main__":
    main()