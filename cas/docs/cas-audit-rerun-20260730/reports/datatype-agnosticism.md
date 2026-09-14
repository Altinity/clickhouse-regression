# datatype-agnosticism — re-run 2026-07-30

Re-run of `cas-datatype-agnosticism-audit.md` (and the adjacent `audit-summary.md` note for
CAS-202 / CAS-107) against `cas-audit-20260730` (HEAD `834c9517f56`, tracks `altinity/cas-gc-rebuild`).

## Scope in current code
- Files/dirs walked: full CAS tree
  `src/Disks/DiskObjectStorage/MetadataStorages/ContentAddressed/**` (111 `.h`/`.cpp` files across
  `Backend/`, `Formats/`, `Gc/`, `Parts/`, `Pool/`, `Primitives/`, `Tools/`, `benchmarks/`, plus
  the four top-level files `ContentAddressed{Metadata,Transaction,Exchange,Settings}.{h,cpp}`).
- Targeted greps (case-insensitive) across the whole CAS tree for any hint of
  data-type awareness:
  - `JSON`, `Variant`, `Dynamic`, `QBit`, `Geo`, `Object`,
  - `DataType*`, `SerializationObject`, `ISerialization`, `escapeForFileName`,
  - column-file-name shapes: `.bin`, `.mrk`, `.cmrk`, `.idx`, `.null`, `dict`,
    `discriminator`, `dynamic_structure`, `object_structure`, `shared_data`.

## Findings still present
None. CAS remains fully data-type agnostic.

## Findings fixed / no longer reproducible
- **CAS-202** — data-type agnosticism (verified). Original verdict was
  "YES, definitively — CAS never interprets column data or types." The current PR code preserves
  every one of the original's three independent guarantees:
  1. **No `#include` of `DataTypes/**` or `SerializationObject.h` anywhere in the CAS tree.** Grep
     for `#include.*DataTypes/`, `SerializationObject`, `DataTypeObject`, `DataTypeVariant`,
     `DataTypeDynamic`, `DataTypeQBit` across all 111 CAS files returns zero matches. CAS never
     depends on the type system compilation unit at all.
  2. **Manifest entry still carries no type field.**
     `src/.../Formats/CasPartManifestFormat.h:50-65`:
     ```
     struct ManifestEntry {
         String path;
         EntryPlacement placement = EntryPlacement::Inline;
         BlobRef ref{};
         uint64_t blob_size = 0;
         String inline_bytes;
         ...
     };
     ```
     Only `path` (opaque string), placement (Inline|Blob), a content-hash `BlobRef`, size, and raw
     bytes. No column/type/serialization identifier.
  3. **Blob keys are still derived purely from the content hash** — file names never become S3 key
     segments.
     `src/.../Formats/CasLayout.cpp:34-37`:
     ```
     String Layout::blobKey(const BlobRef & ref) const
     {
         return shardedKey("blobs/" + String(blobHashAlgoName(ref.algo)), blobHexOf(ref));
     }
     ```
     The only path components are the fixed `"blobs"` prefix, the hash-algorithm name, and the
     content hex. The `path` string from `ManifestEntry` is not spliced into the key.

- **CAS-107** (adjacent — manifest bytes not version-stable; flagged in the original summary as
  "harmless"). Still applies at the framing level (JSON body of the manifest can change across
  versions), still harmless for agnosticism because the JSON encoding is over CAS's own control
  fields (path, placement, blob ref, size) — **not** over any type-derived structure. No CAS code
  encodes/decodes type-tagged bytes. No change of substance since the original audit.

## New findings (not in original audit)
- **NEW-datatype-agnosticism-1** — informational, agnosticism-preserving:
  The original audit's Layer 1 quote used the fields `UInt128 blob_hash{}`. In current code the
  hash + algorithm are packed into a single `BlobRef ref` (`src/.../Formats/CasPartManifestFormat.h:54`),
  and `blobKey` renders the algo as its own key segment (`CasLayout.cpp:36`). This is a
  wire-format refinement (multi-algorithm-per-pool support), **not** a data-type coupling: the
  algorithm axis is over hash functions (city128, sha256, …), not column types. Agnosticism is
  preserved.

- **NEW-datatype-agnosticism-2** — informational:
  The original audit's edge-case table noted that mutable per-part files
  (`uuid.txt`/`txn_version.txt`/`metadata_version.txt`) were "kept out of the content manifest
  (stored per-ref) — independent of column types." Current code has **removed** that special case.
  `src/.../ContentAddressedTransaction.cpp:844-850`:
  > "The former mutable-per-part-file branch (uuid.txt/metadata_version.txt/txn_version.txt
  > staging directly into a separate mutable payload) is DELETED here — these three names fall
  > through to the ordinary content path below like any other tree file. There is no filename left
  > to special-case: `kMutablePerPartFiles`/`isMutablePerPartFile` predicate itself is gone too …"
  Impact on agnosticism: **strengthens it** — one fewer name-based branch. All part files now flow
  through the same content path regardless of whether they carry column data or per-part
  bookkeeping.

- **NEW-datatype-agnosticism-3** — informational, worth naming so future auditors don't mistake
  it for type coupling:
  The **only** place CAS inspects a file's name to alter behavior is
  `Cas::partFileMustStayBlob` (`src/.../ContentAddressedTransaction.cpp:65-73`, declared in
  `ContentAddressedTransaction.h:243`):
  ```
  bool partFileMustStayBlob(std::string_view file_name)
  {
      if (file_name == "primary.idx")
          return true;
      for (std::string_view suffix : {".bin", ".mrk", ".mrk2", ".mrk3", ".cmrk", ".cmrk2", ".cmrk3"})
          if (hasSuffix(file_name, suffix))
              return true;
      return false;
  }
  ```
  This is a **structural** MergeTree-file-shape predicate ("is this a column-data or marks file?"
  → must not be inlined, must go to a content blob so ranged reads keep column-read selectivity),
  applied uniformly to **every** column type. It does not branch on Int vs String vs JSON vs
  Variant vs Dynamic vs QBit vs Geo: every serialization emits `<escaped_name>.bin` + marks, and
  the predicate treats them identically. Documented explicitly at
  `ContentAddressedTransaction.h:239-242`:
  > "Part files that must NOT be inlined into the tree: per-column data (`.bin`) and marks
  > (`.mrk*`/`.cmrk*`) … Everything else (the small eager metadata files) is an inline candidate."
  Not a type dependency — call it out here only to preempt future reviewers finding a suffix list
  and reading it as one.

## By-design / N/A / info
- Occurrences of the word `Variant` in CAS code (`Pool/CasServerRoot.cpp`, `Pool/CasPool.h`,
  benchmark files, etc.) are English usage ("a FORCE variant of the API", "this variant of the
  benchmark") — not `DataTypeVariant`.
- Occurrences of `Object` (e.g. `mountpointObject`, `getNamespaceFile`, `JsonObj`) refer to
  S3-object / JSON-object contexts, not `DataTypeObject`/`SerializationObject`.
- Occurrences of `dynamic` are dynamic dispatch / dynamic memory, not the `Dynamic` column type.
- `discriminator` appears only in CAS's own enum-tag context (owner-kind, token-kind, removal-class
  discriminators inside the CAS protocol) — not `SerializationVariant`'s variant discriminator
  column-file.
- CAS's own `caInspectToJson`, `CasJsonWriter`, and `writeJSONString` usage in
  `Tools/CasInspect.cpp` and `benchmarks/` is JSON-as-a-wire-format for CAS control objects; no
  relation to the `JSON`/`Object('json')` column type.

## Verdict summary table
| CAS-id | Old severity | Status | Evidence anchor |
|---|---|---|---|
| CAS-202 (datatype agnosticism) | verified / N-A (positive finding) | ✅ still holds — re-verified | `Formats/CasPartManifestFormat.h:50-65`, `Formats/CasLayout.cpp:34-37`; zero `#include DataTypes/**` across CAS tree |
| CAS-107 (manifest bytes not version-stable — harmless) | info | ⚪ info — unchanged, still orthogonal to agnosticism | `Formats/CasPartManifestFormat.h` (framing) |
| NEW-datatype-agnosticism-1 (BlobRef packs algo) | — | ⚪ info — agnosticism-preserving refinement | `Formats/CasPartManifestFormat.h:54`, `Formats/CasLayout.cpp:36` |
| NEW-datatype-agnosticism-2 (mutable per-part special case removed) | — | ⚪ info — strengthens agnosticism | `ContentAddressedTransaction.cpp:844-850` |
| NEW-datatype-agnosticism-3 (`partFileMustStayBlob` suffix list — structural, not type-based) | — | 📐 by-design — call-out only | `ContentAddressedTransaction.cpp:65-73`, `.h:239-243` |

## Counts
- Findings still present: **0**
- Findings fixed / no longer reproducible: **0** (nothing to fix — original was a positive
  verification, still verified)
- Re-verified positive findings: **2** (CAS-202, CAS-107)
- New findings: **3** (all informational / by-design; none change the agnosticism verdict)
