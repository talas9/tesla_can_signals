# Derived APE research profile

[ape-hw25-derived.json](ape-hw25-derived.json) records seven independently recovered fields from an older HW2.5 APE image. It is a separate research schema: none of the archived vehicle/bus profiles are changed. Network identity and current HW4 compatibility remain unknown.

Firmware and APE images acquired from Lunars. The evidence comes from offline numeric disassembly, shared-schema reader/writer matching, and emitter packing analysis. Original binaries, original code, raw captures and bulk source definitions are not included.

## Recovered fields

| ID | Mux | Bits | Research label | Verified endpoint |
|---|---:|---|---|---|
| `0x3EE` | 0 | 37 | Visualization request | RoadRunner payload `+0x3d6`, snapshot `+0x3e6` |
| `0x3EE` | 0 | 38 | Stops-control request | Guarded accepted state; RoadRunner snapshot `+0x4dc` |
| `0x3EE` | 1 | 45 | Lane-graph request | Packed `+0x294e` bit8 → RoadRunner snapshot `+0x3d0` |
| `0x3EE` | 0 | 46 | Unnamed raw bit | Packed `+0x2946` bit55 only |
| `0x399` | — | 0–3 | Translated state | ASM snapshot `+0x70` plus other inputs |
| `0x247` | — | 32–38 | Translated abort reason | ASM snapshot `+0x84` |
| `0x5D9` | 2 | 46–52 | Translated check result | ASM snapshot `+0x74`, numeric translation |

Names above are research labels. Bit positions use zero-based little-endian numbering. The `0x3EE` selector occupies bits0–2; `0x5D9` uses bits0–3. Output message lengths are not asserted. A decoder must check that enough payload bytes exist for the selected field and that its mux matches. The recovered `0x3EE` decoder rejects lengths below eight; longer lengths log a diagnostic and continue, so an exact-eight acceptance rule would misrepresent it.

## Proof and interpretation

Each JSON field includes the owning binary, instruction locations, established edge and remaining boundary. These locations identify the inspected older image only; they are not addresses for a matching current release.

- **Requests:** `canrx` decoder `0x2eccc0` dispatches old `0x3EE` mux pages. Bit45 packing at `0x2edcc4`–`0x2edcec` and callback `0x2b2df4` establish the lane-graph shared field. Bit46 ends at packed bit55; its normalized consumer remains open.
- **Accepted stops-control state:** callback `0x2b27a0` conditionally updates state `+0x4cc`; shared publication adds a timestamp header of `0x10`. ASM reads snapshot `+0x4dc` at `0x2b32cc`. This establishes a consumer, not an unconditional acknowledgement or activation.
- **State and abort:** recovered cantx state helper `0x2b5da0` does not emit modern state6. Abort translator `0x2b6300` uses ASM `+0x84`, independently of HOLD's internal reason.
- **Conditional diagnostic:** cantx `0x26c884` reads ASM `+0x74` in a paired load. Translator `0x2b5f90` has 53 entries; input12 maps to12 and unsigned inputs above52 map to45. The ASM branch producing12 requires accepted stops-control state2, additional trajectory/deceleration conditions and earlier guards. Failed conditions continue other checks. No old enum name or current HW4 identity is assigned.

The HOLD-related Boolean at ASM `+0x68` has no proven CAN consumer. It is deliberately absent from the field list. These findings do not provide a dedicated parked TLSSC acknowledgement.

## Schema and validation

This sidecar uses a `messages` array and per-field `evidence`; it is not a drop-in replacement for the compact originals. `length_bytes: null` means unestablished, not zero. Empty `value_description` maps mean that no OEM enum names are asserted. All seven fields are unsigned little-endian raw values with scale1 and offset0.

Run `python3 research/validate_profile.py` from the repository root. Validation checks profile scope, exact recovered tuples, mux and payload boundaries, label uniqueness, evidence presence, and exclusion of modern enum tables. It does not establish runtime compatibility.
