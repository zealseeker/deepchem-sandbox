From ubuntu:latest

RUN apt-get update && \
    apt-get install -y -q wget git libxrender1 libsm6 bzip2 && \
    apt-get clean
    
RUN MINICONDA="Miniconda3-latest-Linux-x86_64.sh" && \
    wget --quiet https://repo.continuum.io/miniconda/$MINICONDA && \
    bash $MINICONDA -b -p /miniconda && \
    rm -f $MINICONDA
ENV PATH /miniconda/bin:$PATH

RUN conda update -n base conda
RUN export LANG=en_US.UTF-8 && \
    git clone https://github.com/deepchem/deepchem.git && \
    cd deepchem && \
    git checkout 2.3.0 && \
    bash scripts/install_deepchem_conda.sh && \
    python setup.py develop

# Clean up
RUN cd deepchem && \
    git clean -fX
    
RUN pwd && python -c "import deepchem; print(deepchem.__version__)"
