# OGS to Anki

This project provides a set of tools to download Go problems (Tsumego) from OGS (Online-Go.com) or Tsumego Hero, convert them into a standardized SGF format, and then generate Anki decks for spaced repetition practice.

This is designed to work with the note type and card template from [TowelSniffer/Anki-go](https://github.com/TowelSniffer/Anki-go). Ensure `var goFirst = true`.

## Directory Structure

*   `src/`: Contains the Python scripts for downloading and converting data.
*   `tests/`: Contains unit tests for the scripts.

## Prerequisites

You can install the dependencies using pip:

```bash
pip install -r requirements.txt
```

## Usage Workflow

### 1. Download Problems

#### From OGS (Online-Go.com)

Use `src/ogs_collection_to_sgf.py` to download a puzzle or a collection of puzzles from OGS.

```bash
# Download a single puzzle
python3 src/ogs_collection_to_sgf.py <PUZZLE_ID> --output <OUTPUT_DIR>

# Download an entire collection
python3 src/ogs_collection_to_sgf.py <PUZZLE_ID> --collection --output <OUTPUT_DIR>
```

#### From Tsumego Hero

Use `src/tsumego_hero_collection_to_sgf.py` to download a collection from Tsumego Hero.

```bash
python3 src/tsumego_hero_collection_to_sgf.py <COLLECTION_URL> --output <OUTPUT_DIR>
```

Example:
```bash
python3 src/tsumego_hero_collection_to_sgf.py https://tsumego.com/sets/view/50/1 --output my_puzzles
```
This will create a subdirectory named after the collection inside `my_puzzles` containing the SGF files.

### 2. Standardize SGF Format (Tsumego Hero only)

Tsumego Hero uses a slightly different SGF marking convention (`C[+]` for correct branches) compared to what the Anki converter expects (OGS style `C[CORRECT]`).

Use `src/convert_tsumego_hero_sgf_to_ogs_format.py` to convert the downloaded Tsumego Hero SGFs.

```bash
python3 src/convert_tsumego_hero_sgf_to_ogs_format.py <PATH_TO_SGF_OR_DIRECTORY>
```

Example:
```bash
python3 src/convert_tsumego_hero_sgf_to_ogs_format.py "my_puzzles/Life & Death - Elementary #1"
```
Use `--backup` to keep original files as `.bak`.

### 3. Generate Anki Import File

Use `src/sgf_to_anki.py` to turn the SGF files into a TSV file suitable for importing into Anki.

```bash
python3 src/sgf_to_anki.py <INPUT_DIRECTORY> <OUTPUT_FILENAME.tsv>
```

Example:
```bash
python3 src/sgf_to_anki.py "my_puzzles/Life & Death - Elementary #1" "Life_and_Death_Elementary.tsv"
```

### 4. Import into Anki

1.  Open Anki.
2.  File -> Import...
3.  Select the generated `.tsv` file.
4.  Map the fields correctly (usually just the SGF content to a specific field on your note type).


## Testing

To run the tests:

```bash
python3 -m unittest discover tests
```
