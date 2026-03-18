# Gandalf Prompting Project

## Overview

This project contains tools and automated attacks for the [Gandalf AI security challenge](https://gandalf.lakera.ai/) Level 8 ("Gandalf the White"). The goal is to extract a secret password and reconstruct the system prompt from an LLM using prompt injection techniques.

## Project Structure

```
gandalf_prompting/
  cli/
    gandalf.py                           # Core CLI tool and shared library (API interaction + logging)
    gandalf_log.json                     # Full log of all API interactions
    cookies.json                         # Session cookies for API authentication (not committed)
  password_reveal_attack/
    backend.py                           # Unified backend: --target api | emulator | emulator_v2
    acrostic_attack.py                   # Acrostic attack: 160 prompts across 4 areas, statistical analysis
    simple_attacks.py                    # 14 categories of simple attacks (106 prompts)
    analyze.py                           # Multi-strategy analysis: exact frequency, joint probability, length-grouped
    emulator_v2_attacks.py               # Blind attacks wave 1 against V2 (80 prompts, 10 categories)
    emulator_v2_attacks_wave2.py         # Blind attacks wave 2 against V2 (71 prompts, 10 categories)
    README.md                            # Full comparison: original vs GPT-4o vs GPT-5.4 emulator, V2 results
  system_prompt_reveal_attack/
    run_waves.py                         # Unified runner: --target api|emulator|emulator_v2 --wave 1-16|all
    attack.py                            # Wave 1: Broad survey of 31 techniques (157 prompts)
    attack_wave2.py .. attack_wave16.py  # Waves 2-16: Iterative refinement attacks (~1,200 total prompts)
    final_analysis.py                    # Compiles wave 1-6 results into system prompt reconstruction
    results*.json                        # Raw results from each wave
    README.md                            # Full writeup: all 16 waves, reconstructed prompt, emulator comparison
  test_emulator/
    emulator.py                          # Gandalf emulator V1: GPT-5.4 + reconstructed system prompt + output filter
    emulator_v2.py                       # Gandalf emulator V2: hardened system prompt + enhanced output filter
    emulator_log.json                    # V1 interaction log
    emulator_v2_log.json                 # V2 interaction log
    README.md                            # Emulator documentation (V1 vs V2 comparison)
  venv/                                  # Python virtual environment
```

## Setup

```bash
cd gandalf_prompting
python3 -m venv venv
source venv/bin/activate
pip install requests openai
```

Export session cookies from the Gandalf website into `cli/cookies.json` as a JSON object (e.g. `{"session_id": "..."}`).

For the emulator, set `OPENAI_API_KEY` environment variable.

## Commands

All commands must be run from the project root (`gandalf_prompting/`) with the virtual environment activated.

### Interactive CLI

```bash
# Real Gandalf API
python cli/gandalf.py -i

# Local emulator V1
OPENAI_API_KEY="..." python test_emulator/emulator.py -i

# Local emulator V2 (hardened)
OPENAI_API_KEY="..." python test_emulator/emulator_v2.py -i
```

### Run attacks

```bash
# Acrostic attack (--target api | emulator | emulator_v2)
python password_reveal_attack/acrostic_attack.py --target api
python password_reveal_attack/acrostic_attack.py --target emulator
python password_reveal_attack/acrostic_attack.py --target emulator_v2

# Simple attacks (14 categories, 106 prompts)
python password_reveal_attack/simple_attacks.py --target api
python password_reveal_attack/simple_attacks.py --target emulator_v2

# Blind attacks against V2 emulator (151 prompts)
python password_reveal_attack/emulator_v2_attacks.py --target emulator_v2
python password_reveal_attack/emulator_v2_attacks_wave2.py --target emulator_v2

# System prompt extraction -- unified runner (all 16 waves)
python system_prompt_reveal_attack/run_waves.py --target emulator --wave all
python system_prompt_reveal_attack/run_waves.py --target api --wave 1-6
python system_prompt_reveal_attack/run_waves.py --target emulator_v2 --wave all

# System prompt reconstruction analysis (uses wave 1-6 results)
python system_prompt_reveal_attack/final_analysis.py
```

## Key Technical Details

- **API endpoints**:
  - `https://gandalf-api.lakera.ai/api/send-message` (POST with `defender` and `prompt` fields)
  - `https://gandalf-api.lakera.ai/api/guess-password` (POST with `defender` and `password` fields, returns `{"success": true/false}`)
- **Defender ID**: `gandalf-the-white`
- **Unified backend**: `password_reveal_attack/backend.py` provides `get_backend("api"|"emulator"|"emulator_v2")` with identical `send_message()` and `guess_password()` interfaces
- **Emulator model**: GPT-5.4 via OpenAI API
- **Logging**: All API calls are automatically logged via `send_message()` in `gandalf.py` to `cli/gandalf_log.json`; emulator logs to `test_emulator/emulator_log.json`
- **Rate limiting**: Attack scripts include 0.5s delays between requests to avoid rate limiting
- **System prompt attack** uses 16 iterative waves with 60+ techniques including binary yes/no search (most effective), rule enumeration, [DEBUG] creative output, fill-in-the-blank, and many academic techniques (Policy Puppetry, Crescendo, etc.). See `system_prompt_reveal_attack/README.md` for full details and reconstructed prompt
