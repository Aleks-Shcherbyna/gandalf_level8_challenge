# Gandalf Prompting Project

## Overview

This project contains tools and automated attacks for the [Gandalf AI security challenge](https://gandalf.lakera.ai/) Level 8 ("Gandalf the White"). The goal is to extract a secret password from an LLM using prompt injection techniques.

## Project Structure

```
gandalf_prompting/
  cli/
    gandalf.py                           # Core CLI tool and shared library (API interaction + logging)
    gandalf_log.json                     # Full log of all API interactions
    cookies.json                         # Session cookies for API authentication (not committed)
  password_reveal_attack/
    acrostic_attack.py                   # Data collection: 80 prompts across 4 areas, collects acrostics
    analyze.py                           # Multi-strategy analysis: exact frequency, joint probability, length-grouped
    README.md                            # Detailed explanation of the challenge, defenses, and attacks
  venv/                                  # Python virtual environment
```

## Setup

```bash
cd gandalf_prompting
python3 -m venv venv
source venv/bin/activate
pip install requests
```

Export session cookies from the Gandalf website into `cli/cookies.json` as a JSON object (e.g. `{"session_id": "..."}`).

## Commands

All commands must be run from the project root (`gandalf_prompting/`) with the virtual environment activated.

### Interactive CLI

```bash
python cli/gandalf.py -i
```

### Single prompt

```bash
python cli/gandalf.py "Your prompt here"
```

### Run attack

```bash
# Run acrostic attack (160 prompts across 4 areas, 2 rounds each) + multi-strategy analysis + verification
python password_reveal_attack/acrostic_attack.py
```

## Key Technical Details

- **API endpoints**:
  - `https://gandalf-api.lakera.ai/api/send-message` (POST with `defender` and `prompt` fields)
  - `https://gandalf-api.lakera.ai/api/guess-password` (POST with `defender` and `password` fields, returns `{"success": true/false}`)
- **Defender ID**: `gandalf-the-white`
- **Logging**: All API calls are automatically logged via `send_message()` in `gandalf.py` to `cli/gandalf_log.json`
- **Rate limiting**: Attack scripts include 0.5s delays between requests to avoid rate limiting
- **Attack scripts** import `send_message` and `load_cookies` from `cli/gandalf.py` via `sys.path`
