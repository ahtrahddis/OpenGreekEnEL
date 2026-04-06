# OpenGreekEnEl Dictionary for Kindle

**OpenGreekEnEl** is a high-quality, comprehensive English-to-Greek dictionary specifically built for Amazon Kindle devices. It leverages structured data from Wiktionary to provide a seamless translation experience for readers of English literature.

## Download

You can find the ready-to-use dictionary file in the `mobi` folder of this repository.

* **Latest Version:** [OpenGreekEnEl_v2.mobi](https://github.com/ahtrahddis/OpenGreekEnEL/raw/refs/heads/main/mobi/OpenGreekEnEl_v2.mobi)

## Features

* **Extensive Vocabulary:** Over 44,000 entries including modern terms, idioms, and specialized terminology.
* **Rich Metadata:** Clearly labeled parts of speech in Greek (e.g., **[Ουσ.]**, **[Ρήμ.]**, **[Επίθ.]**) for grammatical clarity.
* **Contextual Examples:** Includes usage examples in italics to help understand how words are used in real sentences.
* **Optimized for E-Ink:** High-contrast formatting with bold headers and bulleted definitions for easy reading on Kindle screens.
* **Fully Offline:** No internet connection required once installed.

## Installation

1. Connect your Kindle to your computer via USB.
2. Locate the `documents/dictionaries` folder on your Kindle drive.
3. Copy the `OpenGreekEnEl_v2.mobi` file into that folder.
4. Safely eject your Kindle.
5. On your Kindle, go to **Settings** > **Language & Dictionaries** > **Dictionaries** > **English** and select **OpenGreekENEL** as your primary dictionary.

## Technical Details

* **Data Source:** [Wiktionary](https://www.wiktionary.org/) via [kaikki.org](https://kaikki.org).
* **Format:** Mobipocket (MOBI) with Kindle-specific dictionary headers.

## Build Process

The dictionary is generated using a custom Python pipeline:

1. **Parsing:** Raw JSONL data from `kaikki.org` is processed via Python to clean definitions and format entries.
2. **Conversion:** Data is transformed into a Tab-separated format.
3. **Compilation:** Compiled into the final Kindle format using **PyGlossary** and **Amazon KindleGen**.

## License

This project is an independent effort. All dictionary data is provided under the **CC BY-SA 3.0** license. Proper attribution to Wiktionary contributors is maintained within the metadata and cover of the dictionary.
