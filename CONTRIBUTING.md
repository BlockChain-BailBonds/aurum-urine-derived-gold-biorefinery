# Contributing

This repository is currently an access-controlled 918 Technologies research project.

## Required contribution properties

- Preserve the distinction between gold recovery and elemental transmutation.
- Label assumed, simulated, measured, and externally sourced values explicitly.
- Do not add donor identifiers, medical information, raw biospecimen metadata, credentials,
  proprietary partner data, or unreviewed wet-lab procedures.
- Add unit-bearing names to every numeric field.
- Preserve exact gold mass balance and add tests for every model change.
- Cite primary sources for scientific claims and current official sources for requirements.
- Record conflicts of interest and relevant background IP.

## Development

```bash
python -m venv .venv
. .venv/bin/activate
python -m pip install -e ".[dev]"
python -m ruff check .
python -m pytest --cov=aurum_biorefinery --cov-report=term-missing
python -m build
```

## Pull requests

Each pull request must state:

- what changed and why;
- the evidence class of every new performance statement;
- unit and mass-balance impact;
- tests run;
- safety, ethics, privacy, regulatory, and IP implications;
- whether documentation, schema, and examples were updated.

No pull request may silently change a synthetic example into a measured-data claim.

