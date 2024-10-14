FROM continuumio/miniconda3

WORKDIR /app

# biofilter version argument
ARG BIOFILTER_VERSION=2.4.3

RUN apt-get update \
    # install packages needed for PLINK, NEAT plots and biofilter installation
    && apt-get install -y --no-install-recommends libz-dev g++ gcc git wget tar unzip make \
    && rm -rf /var/lib/apt/lists/* \
    # install PLINK
    && wget https://s3.amazonaws.com/plink2-assets/alpha5/plink2_linux_x86_64_20240105.zip \
    && unzip plink2_linux_x86_64_20240105.zip \
    && rm -rf plink2_linux_x86_64_20240105.zip \
    # move plink2 executable to $PATH
    && mv plink2 /usr/bin \
    # install biofilter
    && wget https://github.com/RitchieLab/biofilter/releases/download/Biofilter-${BIOFILTER_VERSION}/biofilter-${BIOFILTER_VERSION}.tar.gz -O biofilter.tar.gz \
    && tar -zxvf biofilter.tar.gz --strip-components=1 -C /app/ \
    && /opt/conda/bin/python setup.py install \
    && chmod a+rx /app/biofilter.py \
    # install python packages needed for pipeline
    && conda install -y -n base -c conda-forge scikit-learn dominate wget libtiff conda-build scipy pandas seaborn matplotlib numpy apsw sqlite \
    && conda clean --all --yes \
    # install NEAT plots
    && git clone https://github.com/PMBB-Informatics-and-Genomics/NEAT-Plots.git \
    && mv NEAT-Plots/manhattan-plot/ /app/ \
    && conda develop /app/manhattan-plot/ \
    # remove NEAT-plots directory and biofilter tarball
    && rm -R NEAT-Plots biofilter.tar.gz

USER root
