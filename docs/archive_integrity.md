# Archive Integrity — SHA256 Checksum Design Notes

**P18.6 | Freeze-Maintenance | 2026-04-17**

---

## What SHA256 Integrity Checks Provide

The `integrity` field in `archive_manifest.json` stores a SHA256 hex digest for each archived file.
This detects:

- **Disk bit-rot / partial writes** — machine-level data drift during storage
- **Accidental file editing** — developer modifies an archived file without updating the manifest
- **One-sided tampering** — file is changed but manifest integrity entry is not updated

---

## What SHA256 Integrity Checks Do NOT Provide

SHA256 is a **collision-resistant hash**, not an **authenticated MAC/signature**.

Specifically, SHA256 integrity CANNOT detect:

- **Coordinated attack**: attacker rewrites both the file AND the `integrity` entry in `manifest.json` simultaneously. Detecting this requires HMAC or asymmetric signing with a secret key outside the archive directory — this is out of P18.6 scope.
- **Deletion of the entire `integrity` dict**: when `integrity` is absent (null/omitted), `validate_workbench_archive_manifest()` skips integrity checks entirely. This is intentional — it maintains backward compatibility with pre-P18.6 archives that have no integrity field. Users should treat "no integrity field" as "integrity not verified" not as "integrity guaranteed clean".

---

## Backward Compatibility

- `integrity` is **optional** in the manifest schema and in validation
- Archives created before P18.6 have no `integrity` field — they pass validation with zero integrity checks
- Archives created after P18.6 always include `integrity` — validation always runs integrity checks on those files

---

## Future Enhancement (Out of Scope for P18.6)

To detect coordinated file + manifest tampering, a future round should consider:

- **HMAC-SHA256**: store `HMAC(secret, file_content)` per file, with the HMAC key stored outside the archive directory (e.g., environment variable or key management service)
- **Asymmetric signing**: private key signs each file digest; public key is distributed separately from the archive

This is explicitly out of P18.6 scope — the current SHA256 approach is appropriate for detecting **accidental** data drift, not adversarial tampering.
