#!/usr/bin/env bash
set -euo pipefail

# Run once inside your repo to set sane defaults for this project
git config core.autocrlf input
git config core.filemode false
git config core.ignorecase false
git config core.symlinks true
git config pull.rebase false
git config init.defaultBranch main

echo "Repo-level git config set."
