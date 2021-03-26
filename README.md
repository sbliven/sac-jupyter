# Jupyter kernel for SaC

This repository contains jupyter-related tools for SaC.

## Installation

Installing the kernel requires the following steps:

1. Install sac with jupyter support.
2. Copy the content of this repository as follows:
```bash
mkdir -p $HOME/.local/share/jupyter/kernels
cp -r sac  $HOME/.local/share/jupyter/kernels/
```
3. Adjust the path in `~/.local/share/jupyter/kernels/sac/kernel.json` to
   point to the location of the `kernel.py` file in this repository.
4. In `kernel.py` adjust the path to `sac2c` line 105.

At some point we hope to add these files to the sac2c packages so the
installation process would be significantly simpler.

## Running

Running sac kernel is as simple as:
```bash
jupyter notebook
```
and in the web interface you set the kernel language to SaC.

On the terminal you can run:
```bash
ipython console --kernel=sac
```
If you do so you may want to install this lexer https://github.com/SacBase/sac-pygments
to get syntax highlighting.

