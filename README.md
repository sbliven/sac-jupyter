# Jupyter kernel for SaC

This repository contains jupyter-related tools for SaC.

## Installation

Installing the kernel requires the following steps:

1. Install sac with jupyter support.
2. Copy the content of this repository to the default location where
   jupyter is looking for kernels. On linux systems local jupyter
   configurations are located in `$HOME/.local/share/jupyter`.
   On OSX this is at `$HOME/Library/Jupyter` and on windows it is
   `%APPDATA%\jupyter`. Referring to the path as <jupyter-path>,
    you should do:
```bash
mkdir -p <jupyter-path>/kernels
cp -r sac <jupyter-path>/kernels
cp -r sac_tutorial <jupyter-path>/kernels
```
3. Adjust the path in `<jupyter-path>/kernels/sac/kernel.json` and in
   `<jupyter-path>/kernels/sac_tutorial/kernel.json` to
   point to the location of the `kernel.py` file in this repository.
4. In `kernel.py` adjust the path to `sac2c` line 105.
5. Install `nbextensions` for jupyter.
6. Now install the tutorial:
```bash
mkdir -p <jupyter-path>/nbextensions/
cp -r nbextensions/* <jupyter-path>/nbextensions
```
7. Enable the tutorial:
```bash
jupyter nbextension enable sac_tutorial/main
```

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

