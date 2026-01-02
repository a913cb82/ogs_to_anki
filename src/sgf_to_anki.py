#!/usr/bin/python
import argparse
import glob
import os
import re


def clean_sgf_comment(comment_text):
    """
    Cleans up an SGF comment string by removing HTML, handling newlines,
    and removing redundant CORRECT/WRONG messages.
    """
    # Replace <br> tags with newlines to be processed later
    comment_text = re.sub(r'<br\s*/?>', '\n', comment_text, flags=re.IGNORECASE)
    # Remove all other HTML tags
    comment_text = re.sub(r'<[^>]*>', '', comment_text)
    # Split by newlines, strip whitespace, and filter empty lines
    parts = [p.strip() for p in comment_text.split('\n') if p.strip()]
    
    # Remove duplicate CORRECT/WRONG messages (e.g., "CORRECT\n<b>CORRECT!</b>")
    if len(parts) > 1:
        first_part_upper = parts[0].upper()
        if first_part_upper in ['CORRECT', 'WRONG']:
            # If the second part starts with the same keyword, remove the keyword from the second part
            if parts[1].upper().startswith(first_part_upper):
                # Remove the keyword (and potential punctuation/space) from the beginning of the second part
                pattern = re.compile(r'^\s*' + re.escape(first_part_upper) + r'[.!\s]*', re.IGNORECASE)
                parts[1] = pattern.sub('', parts[1]).strip()
                if not parts[1]: # If the second part became empty after removal, pop it
                    parts.pop(1)

    # Join with ". "
    cleaned_comment = ". ".join(parts)
    return cleaned_comment


def process_sgf_content(sgf_content):
    """
    Processes SGF content to make it suitable for Anki import.
    - Cleans up comments (C[...]) using clean_sgf_comment.
    - Removes all other newlines from the SGF.
    """
    def replace_comment_match(match):
        return f'C[{clean_sgf_comment(match.group(1))}]'

    # Process comments first
    processed_sgf = re.sub(r'C\[(.*?)\]', replace_comment_match, sgf_content, flags=re.DOTALL)
    # Then remove all newlines from the whole file
    processed_sgf = processed_sgf.replace('\n', '')
    return processed_sgf


def natural_sort_key(s):
    """
    Key for natural sorting (e.g., '1' < '2' < '10').
    Splits the string into text and numeric chunks.
    """
    return [int(text) if text.isdigit() else text.lower()
            for text in re.split('([0-9]+)', s)]


def main():
    parser = argparse.ArgumentParser(
        description='Convert a directory of SGF files to a TSV file for Anki import.'
    )
    parser.add_argument('input_dir', help='Directory containing the SGF files.')
    parser.add_argument('output_file', help='Path to the output TSV file.')
    args = parser.parse_args()

    if not os.path.isdir(args.input_dir):
        print(f"Error: Input directory not found at '{args.input_dir}'")
        return

    sgf_files = glob.glob(os.path.join(args.input_dir, '*.sgf'))
    sgf_files.sort(key=natural_sort_key)

    with open(args.output_file, 'w', encoding='utf-8') as tsv_file:
        for sgf_file_path in sgf_files:
            with open(sgf_file_path, 'r', encoding='utf-8') as sgf_file:
                content = sgf_file.read()
                processed_content = process_sgf_content(content)
                tsv_file.write(processed_content + '\n')

    print(f"Successfully created '{args.output_file}' with {len(sgf_files)} SGF files.")


if __name__ == '__main__':
    main()
