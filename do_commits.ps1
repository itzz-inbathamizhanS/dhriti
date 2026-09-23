git add 00_PROJECT_MASTER/ 01_LITERATURE/ 02_BIOLOGY/ 03_QUANTUM/ 07_NOVELTY/
git commit -m "docs: initialize research and project documentation"

git add pyproject.toml requirements.txt src/dhriti/core src/dhriti/parser
git commit -m "feat: setup core package architecture and QASM parser"

git add src/dhriti/detection src/dhriti/localization
git commit -m "feat: implement fault detection oracle and SBFL localizer"

git add src/dhriti/characterization
git commit -m "feat: implement topological and fault feature extraction"

git add src/dhriti/selection
git commit -m "feat: implement ML selector and bio-pathway baselines"

git add src/dhriti/repair
git commit -m "feat: implement 8 repair operators and stochastic candidate generator"

git add src/dhriti/verification src/dhriti/memory
git commit -m "feat: implement semantic validator and feedback memory"

git add src/dhriti/benchmark
git commit -m "feat: add dataset generation and mutation engine"

git add src/dhriti/cli.py src/dhriti/__init__.py
git commit -m "feat: implement full command-line interface"

git add tests/
git commit -m "test: add end-to-end smoke tests"

git add experiments/ 06_EXPERIMENTS/
git commit -m "chore: conduct k-fold experiments and Bugs4Q real-world evaluation"

git add 08_DOCUMENTATION/ 09_EVIDENCE/ README.md .gitignore
git commit -m "docs: add paper draft, architecture docs, and updated README"
