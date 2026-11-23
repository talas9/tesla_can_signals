# tesla_can_signals
Archived compact signal catalogs in the Model 3, Y, S and X folders, plus a separate APE research profile.

> **Looking for versioned DBC files?** See **[tesla-can-signal-db](https://github.com/talas9/tesla-can-signal-db)** for Model 3 / Model Y definitions organized by source firmware and bus, with bit layouts, scaling, value tables and a searchable index. Its coverage does not establish Model S/X or HW4 compatibility.

## Scope

The compact originals were [imported on September 10, 2023](https://github.com/talas9/tesla_can_signals/commit/847fe2e). That is a repository date, **not a vehicle firmware version**. They are preserved as an archive; model folders alone do not establish applicability to every model year, hardware generation or current firmware.

The compact JSON `version` field (for example, `3.0.0`) is catalog metadata, not a verified Tesla vehicle software release. Check each file's product, bus and field definitions before using it. This repository is not a complete current HW4 decoder.

## Firmware-extracted Odin data

`firmware/<version>/<Model>/` holds Odin diagnostic data extracted from that Tesla firmware release (Model 3 and Model Y only): `legacy_self_test_parser.json`, `di_swap_rules.json`, `nodes.json`, `bus-alerts-map.json` and `config-options.json`. Versions present: `2026.26.6.5` and `2025.20.8`. The `legacy_self_test_parser.json` is byte-identical between these two versions and between Model 3 and Model Y; the other files differ.

`config-options.json` is the **decoded** gateway option schema: `options` maps each config key (for example `exteriorColor`, `wheelType`) to its option code values. The firmware ships these hashed (`keyHash = SHA256(key + salt)`, `valueHash = SHA256(value + key + salt)`), so decoding is a wordlist match; hashes that match nothing are kept under `undecoded`, and `coverage` states how many keys and values were decoded. `tools/decode_config_options.py` reproduces the decoding from a hashed file and a wordlist.

The top-level `Model3/`, `ModelS/`, `ModelX/` and `ModelY/` folders remain the original 2023 dump, unchanged. Their `legacy_self_test_parser.json` files differ from the firmware copies.

## Research profiles

- [Derived older HW2.5 APE fields](research/README.md) — **4 message IDs / 7 fields** recovered through static analysis, with evidence and remaining limits for each field. This uses a separate schema and leaves the compact originals unchanged. Its network identity and current HW4 compatibility are unverified; receiver consumption does not prove feature activation.

Validate this profile with `python3 research/validate_profile.py`. Passing validation checks the documented profile structure and field boundaries, not compatibility with a live vehicle.

## Related

- [tesla-can-signal-db](https://github.com/talas9/tesla-can-signal-db) — structured CAN signal database and DBC files (Model 3 / Model Y)
- [tesla_odj](https://github.com/talas9/tesla_odj) — Tesla ODJ decoder
- [tesla-ape-research](https://github.com/talas9/tesla-ape-research) — investigation timeline, evidence, corrections and open questions
