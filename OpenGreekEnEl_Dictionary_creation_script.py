import json
import html
from collections import defaultdict
import re

# File names
file_en = "kaikki.org-dictionary-English.jsonl"
file_el = "kaikki.org-dictionary-Greek.jsonl"
output_file = "OpenGreekEnEl_Dictionary.txt"

# Dictionary structure: headword -> list of entries (each with pos, translations, examples, notes)
dictionary = defaultdict(list)

# Extended POS labels - all abbreviated for consistency
pos_labels = {
    "noun": "Ουσ.", "verb": "Ρήμ.", "adj": "Επίθ.", "adv": "Επίρ.",
    "pron": "Αντων.", "prep": "Πρόθ.", "det": "Προσδ.", "conj": "Σύνδ.",
    "intj": "Επιφ.", "num": "Αριθμ.", "part": "Μόρ.", "particle": "Μόρ.",
    "suffix": "Επιθημ.", "prefix": "Προθημ.", "affix": "Πρόσφ.", 
    "name": "Ον.", "proper": "Κυρ.Ον.", "phrase": "Φρ.", "idiom": "Ιδιωτ.",
    "article": "Άρθρ.", "participle": "Μετοχ.", "proverb": "Παροιμ."
}

def clean_text(text):
    """Clean and decode HTML entities"""
    if not text: return ""
    # Decode HTML entities (e.g., &amp; -> &)
    text = html.unescape(text)
    # Remove excessive whitespace
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def is_greek(text):
    """Check if the text contains Greek characters"""
    if not text: return False
    return any('\u0370' <= c <= '\u03ff' or '\u1f00' <= c <= '\u1fff' for c in text)

def clean_headword(word):
    """Clean headword by removing parentheses, prefixes, and other junk"""
    if not word: return ""
    
    # Remove leading parenthetical content like "(astronomy): " or "(bad, ineffectual) "
    # Pattern: (anything): word or (anything) word
    word = re.sub(r'^\([^)]+\):?\s*', '', word)
    
    # Remove quotes
    word = word.strip('"').strip("'")
    
    # Clean whitespace
    word = word.strip()
    
    return word

def is_valid_english_headword(word):
    """Check if this is a valid English headword"""
    if not word: return False
    
    # Must contain at least one Latin letter
    if not any('a' <= c <= 'z' or 'A' <= c <= 'Z' for c in word):
        return False
    
    # Skip if starts with dash (suffix)
    if word.startswith('-'):
        return False
    
    # Skip if contains Greek
    if is_greek(word):
        return False
    
    # Skip if it's just punctuation or numbers
    if all(not c.isalpha() for c in word):
        return False
    
    # Skip if contains any digits
    if any(c.isdigit() for c in word):
        return False
    
    return True

def extract_examples(sense_data):
    """Extract all examples from a sense"""
    examples = []
    if "examples" in sense_data:
        for ex in sense_data["examples"]:
            if ex.get("text"):
                example_text = clean_text(ex.get("text"))
                # Some examples have English translation
                if ex.get("english"):
                    eng = clean_text(ex.get("english"))
                    example_text = f"{example_text} ({eng})"
                examples.append(example_text)
    return examples

def extract_glosses(sense_data):
    """Extract glosses (definitions) from a sense"""
    glosses = []
    if "glosses" in sense_data:
        for gloss in sense_data["glosses"]:
            if gloss:
                glosses.append(clean_text(gloss))
    # Alternative: raw_glosses
    if not glosses and "raw_glosses" in sense_data:
        for gloss in sense_data["raw_glosses"]:
            if gloss:
                glosses.append(clean_text(gloss))
    return glosses

def extract_form_of(sense_data):
    """Extract 'form_of' information (e.g., plural of, past tense of)"""
    forms = []
    if "form_of" in sense_data:
        for form in sense_data["form_of"]:
            if form.get("word"):
                forms.append(clean_text(form.get("word")))
    return forms

def extract_tags(sense_data):
    """Extract grammatical/usage tags"""
    tags = []
    if "tags" in sense_data:
        tags = [clean_text(tag) for tag in sense_data["tags"] if tag]
    return tags

def process_english_file():
    """Process English->Greek translations"""
    print(f"Reading {file_en}...")
    count = 0
    skipped = 0
    
    try:
        with open(file_en, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line)
                    word = clean_text(data.get("word", ""))
                    
                    # Clean the headword (remove parentheses, etc.)
                    word = clean_headword(word)
                    
                    if not is_valid_english_headword(word):
                        skipped += 1
                        continue
                    
                    pos = data.get("pos", "unknown")
                    pos_key = pos.split()[0].lower() if pos else "unknown"
                    pos_label = pos_labels.get(pos_key, pos_key.capitalize())
                    
                    # Process each sense (meaning)
                    for sense in data.get("senses", []):
                        # Extract Greek translations
                        translations = []
                        for tr in sense.get("translations", []):
                            if tr.get("code") == "el" and tr.get("word"):
                                trans_word = clean_text(tr.get("word"))
                                # Some translations have notes
                                note = clean_text(tr.get("note", ""))
                                translations.append({
                                    "word": trans_word,
                                    "note": note
                                })
                        
                        if not translations:
                            continue
                        
                        # Extract all available data
                        examples = extract_examples(sense)
                        glosses = extract_glosses(sense)
                        tags = extract_tags(sense)
                        form_of = extract_form_of(sense)
                        
                        # Store entry
                        entry = {
                            "pos": pos_label,
                            "translations": translations,
                            "examples": examples,
                            "glosses": glosses,
                            "tags": tags,
                            "form_of": form_of
                        }
                        
                        dictionary[word].append(entry)
                        count += 1
                
                except json.JSONDecodeError:
                    print(f"Warning: JSON error on line {line_num}")
                    continue
                except Exception as e:
                    print(f"Warning: Error on line {line_num}: {e}")
                    continue
                
                # Progress indicator
                if line_num % 10000 == 0:
                    print(f"  Processed {line_num} lines, found {count} entries, skipped {skipped}")
        
        print(f"Complete: English file - {count} entries from {line_num} lines")
        
    except FileNotFoundError:
        print(f"Error: {file_en} not found.")

def process_greek_file():
    """Process Greek->English (inverse lookups)"""
    print(f"Reading {file_el}...")
    count = 0
    
    try:
        with open(file_el, "r", encoding="utf-8") as f:
            for line_num, line in enumerate(f, 1):
                try:
                    data = json.loads(line)
                    greek_word = clean_text(data.get("word", ""))
                    
                    if not greek_word or not is_greek(greek_word):
                        continue
                    
                    pos = data.get("pos", "unknown")
                    pos_key = pos.split()[0].lower() if pos else "unknown"
                    pos_label = pos_labels.get(pos_key, pos_key.capitalize())
                    
                    # Process each sense
                    for sense in data.get("senses", []):
                        glosses = extract_glosses(sense)
                        examples = extract_examples(sense)
                        tags = extract_tags(sense)
                        
                        # Use glosses as English headwords
                        for gloss in glosses:
                            # Clean the gloss first
                            english_word = clean_headword(gloss.lower())
                            
                            # Only accept short phrases (1-4 words) as headwords
                            words = english_word.split()
                            if len(words) > 4 or len(words) == 0:
                                continue
                            
                            # Must be English (no Greek characters)
                            if is_greek(english_word):
                                continue
                            
                            # Clean up common patterns that aren't good headwords
                            if english_word.startswith("to ") and len(words) > 2:
                                continue  # Skip "to be able to do"
                            
                            if not is_valid_english_headword(english_word):
                                continue
                            
                            # Create entry
                            entry = {
                                "pos": pos_label,
                                "translations": [{"word": greek_word, "note": ""}],
                                "examples": examples,
                                "glosses": [],
                                "tags": tags,
                                "form_of": []
                            }
                            
                            dictionary[english_word].append(entry)
                            count += 1
                
                except json.JSONDecodeError:
                    continue
                except Exception:
                    continue
                
                # Progress indicator
                if line_num % 10000 == 0:
                    print(f"  Processed {line_num} lines, found {count} entries")
        
        print(f"Complete: Greek file - {count} entries from {line_num} lines")
        
    except FileNotFoundError:
        print(f"Error: {file_el} not found.")

def merge_duplicate_entries(entries):
    """Merge entries with same POS to avoid repetition"""
    merged = {}
    
    for entry in entries:
        pos = entry["pos"]
        if pos not in merged:
            merged[pos] = {
                "translations": [],
                "examples": [],
                "glosses": [],
                "tags": set(),
                "form_of": []
            }
        
        # Add translations (avoid duplicates)
        for trans in entry["translations"]:
            if trans not in merged[pos]["translations"]:
                merged[pos]["translations"].append(trans)
        
        # Add examples (limit to avoid bloat)
        for ex in entry["examples"]:
            if ex not in merged[pos]["examples"] and len(merged[pos]["examples"]) < 5:
                merged[pos]["examples"].append(ex)
        
        # Add glosses
        for gloss in entry["glosses"]:
            if gloss not in merged[pos]["glosses"]:
                merged[pos]["glosses"].append(gloss)
        
        # Add tags
        merged[pos]["tags"].update(entry["tags"])
        
        # Add form_of
        for form in entry["form_of"]:
            if form not in merged[pos]["form_of"]:
                merged[pos]["form_of"].append(form)
    
    return merged

def format_entry(headword, entries):
    """Format a complete dictionary entry for Kindle with cleaner block separation"""
    merged = merge_duplicate_entries(entries)
    formatted_parts = []

    for pos, data in merged.items():
        lines = []

        # First line: POS + translations
        trans_list = []
        for trans in data["translations"]:
            if trans["note"]:
                trans_list.append(f"{trans['word']} <i>({trans['note']})</i>")
            else:
                trans_list.append(trans["word"])

        first_line = f"<div class='pos-section'><b>[{pos}]</b>"
        if trans_list:
            first_line += f" {', '.join(trans_list)}"
        first_line += "</div>"
        lines.append(first_line)

        # Form-of info
        if data["form_of"]:
            forms = ", ".join(data["form_of"])
            lines.append(f"<div><small><i>[μορφή του: {forms}]</i></small></div>")

        # Tags
        if data["tags"]:
            tags = ", ".join(sorted(data["tags"]))
            lines.append(f"<div><small><i>[{tags}]</i></small></div>")

        # Glosses
        if data["glosses"]:
            gloss_text = "; ".join(data["glosses"][:2])
            lines.append(f"<div><small><i>({gloss_text})</i></small></div>")

        # Examples
        if data["examples"]:
            kept = 0
            for example in data["examples"]:
                example = clean_text(example)

                # Kopa poly megala paradeigmata
                if len(example) > 180:
                    continue

                lines.append(f"<div class='example'>• {example}</div>")
                kept += 1

                if kept >= 2:
                    break

        formatted_parts.append("".join(lines))

    return "<div class='entry'>" + "".join(formatted_parts) + "</div>"

def write_output():
    """Write the final dictionary file"""
    print(f"Writing to {output_file}...")
    
    total_headwords = len(dictionary)
    
    try:
        with open(output_file, "w", encoding="utf-8") as out:
            for headword in sorted(dictionary.keys()):
                formatted = format_entry(headword, dictionary[headword])
                out.write(f"{headword}\t{formatted}\n")
        
        print(f"Success! Total headwords: {total_headwords}")
        
        # Statistics
        total_entries = sum(len(entries) for entries in dictionary.values())
        print(f"Statistics:")
        print(f"   - Total headwords: {total_headwords}")
        print(f"   - Total entries: {total_entries}")
        print(f"   - Average entries per headword: {total_entries/total_headwords:.2f}")
        
    except Exception as e:
        print(f"Error writing file: {e}")

# Main execution
if __name__ == "__main__":
    print("=" * 60)
    print("OpenGreek Dictionary Builder - Enhanced Version")
    print("=" * 60)
    
    process_english_file()
    print()
    process_greek_file()
    print()
    write_output()
    
    print("\n" + "=" * 60)
    print("Complete!")
    print("=" * 60)
