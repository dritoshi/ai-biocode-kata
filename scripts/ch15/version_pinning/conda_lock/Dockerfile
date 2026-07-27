FROM condaforge/miniforge3:24.3.0-0@sha256:f412616c712b00c09b4fdfd3001941d1876dfed5ab821bcf1e48ada60b70b7cb AS builder

RUN python -m pip install --no-cache-dir conda-lock==4.0.0
COPY rnaseq.conda-lock.yml /tmp/rnaseq.conda-lock.yml
RUN conda-lock install --prefix /opt/rnaseq /tmp/rnaseq.conda-lock.yml

FROM condaforge/miniforge3:24.3.0-0@sha256:f412616c712b00c09b4fdfd3001941d1876dfed5ab821bcf1e48ada60b70b7cb
COPY --from=builder /opt/rnaseq /opt/rnaseq
ENV PATH="/opt/rnaseq/bin:$PATH"
CMD ["python", "-c", "import Bio; print(Bio.__version__)"]
