#!/bin/bash
# Compile l'étude en PDF (pandoc + XeLaTeX). Usage : bash etude/compiler.sh
set -e
cd "$(dirname "$0")"
ORDRE="00_avant_propos 01_introduction 02_theorie 03_architecture 04_equations 05_donnees 06_programmes 07_transmission \
08_europe 09_resultats 10_distribution 11_comportements 12_robustesse 13_discussion 14_conclusion \
89_appendix 90_annexe_a 91_annexe_b 94_annexe_c 92_annexe_d_bibliographie 96_annexe_e 97_annexe_f 98_annexe_g 99_annexe_h \
93_annexe_i_glossaire 95_annexe_j_reproduction 9k_annexe_k"
FICHIERS=""
mkdir -p build/src
for f in $ORDRE; do
  if [ -f "chapitres/$f.md" ]; then
    # exposants Unicode absents des polices : convertis en \textsuperscript
    sed -e 's/ᵉ/\\textsuperscript{e}/g' -e 's/ʳ/\\textsuperscript{r}/g' -e 's/ᵈ/\\textsuperscript{d}/g' "chapitres/$f.md" > "build/src/$f.md"
    FICHIERS="$FICHIERS build/src/$f.md"
  else echo "absent : $f"; fi
done
pandoc metadonnees.yaml $FICHIERS -o build/etude.tex --standalone --pdf-engine=xelatex --top-level-division=chapter \
  --resource-path=.:figures -f markdown+raw_tex+tex_math_dollars+pipe_tables+implicit_figures
pandoc metadonnees.yaml $FICHIERS -o build/etude.pdf --pdf-engine=xelatex --top-level-division=chapter \
  --resource-path=.:figures -f markdown+raw_tex+tex_math_dollars+pipe_tables+implicit_figures 2> build/compilation.log || \
  { tail -40 build/compilation.log; exit 1; }
echo "PDF : etude/build/etude.pdf ($(du -h build/etude.pdf | cut -f1))"
