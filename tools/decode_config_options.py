#!/usr/bin/env python3
"""Decode a hashed Tesla gateway config-options file with a wordlist.

The gateway ships its configuration schema hashed, as
    {"salt": "<salt>", "hashed": {"<keyHash>": ["<valueHash>", ...], ...}}
where, for a config key K and a value code V:
    keyHash   = SHA256(K + salt)            (hex)
    valueHash = SHA256(V + K + salt)        (hex)
(strings are concatenated as UTF-8 text). The hashes cannot be reversed, so
decoding is a dictionary attack: hash every candidate word and keep the ones
that match. Keys are tried first; for every decoded key the candidate values
are hashed together with that key and compared with the key's value hashes.

Candidate words come from any text/JSON files you pass with --words (tokens
matching [A-Za-z0-9_]+ are extracted), for example a signal database, firmware
strings or a list of known option names. For each token the lowercase-first
camelCase form of UPPER_SNAKE / snake_case names and the last "_" segment are
also tried as key candidates. Hashes that match nothing stay in the output, so
the coverage numbers are honest.

Output (JSON): firmware/model labels, salt, coverage, options
(decodedKey -> sorted value codes) and undecoded (key hashes + counts of
value hashes still unknown).

Usage:
    python3 decode_config_options.py hashed.json --words words.txt more.json \\
        --firmware 2026.26.6.5 --model Model3 -o config-options.json

Standard library only.
"""
import argparse
import hashlib
import json
import re
import sys

TOKEN = re.compile(r"[A-Za-z0-9_]+")


def sha(s):
    return hashlib.sha256(s.encode()).hexdigest()


def load_tokens(paths):
    tokens = set()
    for p in paths:
        with open(p, encoding="utf-8", errors="replace") as f:
            tokens.update(TOKEN.findall(f.read()))
    return tokens


def key_candidates(tokens):
    keys = set(tokens)
    for t in tokens:
        parts = t.split("_")
        if len(parts) > 1:
            keys.add(parts[-1])
            keys.add(parts[0].lower() + "".join(p.capitalize() for p in parts[1:]))
    return keys


def decode(hashed, salt, tokens):
    keys = key_candidates(tokens)
    khmap = {sha(k + salt): k for k in keys}
    options, undecoded_values, undecoded_keys = {}, {}, []
    for kh, vhashes in hashed.items():
        key = khmap.get(kh)
        if key is None:
            undecoded_keys.append(kh)
            if vhashes:
                undecoded_values[kh] = len(vhashes)
            continue
        vmap = {sha(v + key + salt): v for v in tokens}
        found = sorted({vmap[vh] for vh in vhashes if vh in vmap})
        options[key] = found
        missing = sum(1 for vh in vhashes if vh not in vmap)
        if missing:
            undecoded_values[key] = missing
    return options, sorted(undecoded_keys), undecoded_values


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("hashed", help="hashed config-options JSON ({salt, hashed})")
    ap.add_argument("--words", nargs="+", required=True, help="wordlist files (text or JSON)")
    ap.add_argument("--firmware", default="", help="firmware version label for the output")
    ap.add_argument("--model", default="", help="model label for the output")
    ap.add_argument("-o", "--output", help="output file (default: stdout)")
    a = ap.parse_args()

    with open(a.hashed) as f:
        src = json.load(f)
    salt, hashed = src["salt"], src["hashed"]
    options, und_keys, und_vals = decode(hashed, salt, load_tokens(a.words))
    out = {
        "firmware": a.firmware,
        "model": a.model,
        "salt": salt,
        "coverage": {
            "keys_decoded": len(options),
            "keys_total": len(hashed),
            "values_decoded": sum(len(v) for v in options.values()),
            "values_total": sum(len(v) for v in hashed.values()),
        },
        "options": dict(sorted(options.items())),
        "undecoded": {"key_hashes": und_keys, "value_hashes": dict(sorted(und_vals.items()))},
    }
    text = json.dumps(out, indent=2, sort_keys=True) + "\n"
    if a.output:
        with open(a.output, "w") as f:
            f.write(text)
    else:
        sys.stdout.write(text)
    print(json.dumps(out["coverage"]), file=sys.stderr)


if __name__ == "__main__":
    main()
