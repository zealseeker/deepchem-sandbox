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
RUN pip install scikit-learn==0.22 && \
    conda install -y -c rdkit rdkit
    pip install joblib pandas tensorflow pillow deepchem

RUN pwd && python -c "import deepchem; print(deepchem.__version__)"
