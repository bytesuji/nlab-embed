# nlab-embed

- The complete nLab scrape is [here](https://alberts-junk.s3.us-east-2.amazonaws.com/nlab.tar.bz2)
    - also in [database form](https://alberts-junk.s3.us-east-2.amazonaws.com/files_full2.db), used by the lookup script
- There's also a [hnswlib index](https://alberts-junk.s3.us-east-2.amazonaws.com/nlab_vectors.idx) created from the embeddings

## scripts
- `lookup.py` is used to query the database
- `api.py` serves the front-end and API
- `multiembed.py` is for running the embedding job
    - TODO this currently truncates documents at 512 tokens which needs to be fixed
- `extract.py` pulls text out of PDFs and HTML from the raw scrape
