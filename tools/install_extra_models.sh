#!/bin/bash
# Installs the programs used by the extra genomic prediction models of 02_genomic_prediction.Rmd
# (extra_models = true): BayesRCO (BayesR and BayesRC) and JWAS (Julia).
# MTG2 and DMU are distributed by their authors as executables and are not installed here.
# Usage: tools/install_extra_models.sh <install folder>     (default /opt)
set -e
DEST=${1:-/opt}
HERE=$(cd "$(dirname "$0")" && pwd)

# 1. BayesRCO (Mollandin et al. 2022), Fortran; the commit used for the reported results
git clone https://github.com/fmollandin/BayesRCO.git "$DEST/bayesrco_src"
cd "$DEST/bayesrco_src" && git checkout f618a51bc9dbe22bbffe775ea1b3908aea02ed12 && cd src
gfortran -O3 -o bayesRCO RandomDistributions.f90 baymodsRCO.f90 bayesRCO.f90   # module order matters
mkdir -p "$DEST/bayesrco" && cp bayesRCO "$DEST/bayesrco/"

# 2. Julia 1.10.4 from conda-forge (any official Julia 1.10 build works as well)
micromamba create -y -p "$DEST/julia_env" -c conda-forge julia=1.10.4

# 3. JWAS 2.4.0 with the exact package versions used (tools/julia_env/Manifest.toml).
#    Two settings in these files matter:
#    - Distributions is pinned to 0.25.80: JWAS 2.4.0 allows StatsBase up to 0.33 only, and later
#      Distributions releases expect StatsBase 0.34 (the pair fails inside JWAS with
#      "params is not defined for Distributions.Beta").
#    - LocalPreferences.toml turns off the precompile workload of HTTP.jl, which hung behind a proxy.
export JULIA_DEPOT_PATH="$DEST/julia_depot"
mkdir -p "$JULIA_DEPOT_PATH/environments/v1.10"
cp "$HERE/julia_env/"*.toml "$JULIA_DEPOT_PATH/environments/v1.10/"
"$DEST/julia_env/bin/julia" -e 'using Pkg; Pkg.instantiate(); Pkg.precompile(); using JWAS, CSV, DataFrames; println("JWAS ready")'

echo "Set in 02_genomic_prediction.Rmd: bayesrco_bin = $DEST/bayesrco/bayesRCO, julia_bin = $DEST/julia_env/bin/julia, julia_depot = $DEST/julia_depot"
