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
    acrostic_attack_area_search.py       # Step 1: Wide scan of 20 prompt framings to find best areas
    acrostic_attack.py                   # Step 2+3: Targeted attack across best areas + statistical analysis
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

### Run attacks

```bash
# Step 1: Area search -- test 20 different prompt framings to find which areas bypass defenses
python password_reveal_attack/acrostic_attack_area_search.py

# Step 2+3: Targeted acrostic attack across best areas + statistical password analysis
python password_reveal_attack/acrostic_attack.py
```

## Key Technical Details

- **API endpoint**: `https://gandalf-api.lakera.ai/api/send-message` (POST with `defender` and `prompt` fields)
- **Defender ID**: `gandalf-the-white`
- **Logging**: All API calls are automatically logged via `send_message()` in `gandalf.py` to `cli/gandalf_log.json`
- **Rate limiting**: Attack scripts include 0.5s delays between requests to avoid rate limiting
- **Attack scripts** import `send_message` and `load_cookies` from `cli/gandalf.py` via `sys.path`
