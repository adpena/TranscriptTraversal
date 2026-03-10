# TranscriptTraversal

TranscriptTraversal is a small Flask-based utility for turning 2020 Democratic primary debate transcripts into more structured, machine-usable data.

The project was built around transcripts published by The New York Times and exposes two simple workflows:

- convert a source transcript URL into structured JSON
- generate basic word-count summaries from the same source

## Repository Layout

- `app.py`: Flask entrypoint and web form handlers
- `transcript_traversal.py`: transcript parsing and transformation logic
- `templates/` and `static/`: web UI assets
- `exploratory_analysis/`: supporting analysis notebooks and experiments

## Run Locally

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python app.py
```

Then open `http://127.0.0.1:5000/` in your browser.

## License

MIT. See [LICENSE](LICENSE).
