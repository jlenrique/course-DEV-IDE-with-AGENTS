# Pronunciation Management

## Why It Matters

Medical terminology is a first-order quality requirement. Repeated mispronunciation should be handled with pronunciation dictionaries, not manual respelling inside the script.

## Workflow

1. Collect recurring medical terms and approved pronunciations.
2. Build a `.pls` dictionary using IPA or CMU phonemes.
3. Upload the dictionary with `create_pronunciation_dictionary_from_file`.
4. Pass `pronunciation_dictionary_locators` in narration or dialogue requests.
5. Verify pronunciation during smoke checks and downstream QA.

## Model Constraint

- Phoneme tags are documented as working with `eleven_flash_v2` and `eleven_monolingual_v1`.
- For other models or non-English use cases, use alias-style replacements conservatively.

## Minimum Story 3.4 Proof

Story `3.4` should prove the workflow with at least 10 medical terms in a generated `.pls` file and verified upload support, even if live pronunciation review remains a focused smoke check rather than a large regression suite.
