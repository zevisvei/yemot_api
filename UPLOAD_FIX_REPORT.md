# UploadFile — investigation & fix report

_Date: 2026-06-24 · scope: `Yemot.upload_file` / `AsyncYemot.upload_file`_

## 1. Reported problem

- Files **< 50 MB** upload to the correct path — fine.
- Files **> 50 MB** do **not** land at the correct path when **auto-numbering is OFF**.
- Observed result for a 75 MB file:

```python
ins.upload_file(path="677/000.wav", blob=content, file_name="000",
                convert_audio=True, auto_numbering=False)
# -> UploadFile(path='ivr/677/000.wav/000/000.wav', ...)   # nested, wrong
```

A later attempt crashed instead:

```
ValidationError ... UploadFile  (path / size  Field required)
# server returned {'responseStatus': 'ERROR', ..., 'success': False}
```

## 2. How uploads work

`UploadFile` has **two protocols** with **opposite** `path` semantics (the difference
is the whole bug). Confirmed against the live API and against the website client
(`web/.../static/js/buttons/UploadFile.js`, fine-uploader).

| Protocol | When | `path` means | Filename from | Server size cap |
|---|---|---|---|---|
| **Simple** (single multipart, field `file`) | small files | **full file path** (dir + name) | the `path` itself | **~64 MB** (60 MB ok, 70 MB rejected) |
| **Chunked** (fine-uploader: `qqfile` + `qquuid`/`qqpartindex`/… then `?done`) | large files | **directory** | `qqfilename` | very large |

The website **always** uses the chunked protocol (even tiny files) and sends
`path`=directory, `qqfilename`=real name, `convertAudio:0`, `autoNumbering` per checkbox.

### Empirically mapped behavior

Simple endpoint (`path` variations):

| `path` | result |
|---|---|
| `ivr2:zztest` (dir) | ❌ `"path is invalid"` |
| `ivr2:zztest/` (dir) | ❌ `"path is invalid"` |
| `ivr2:zztest/000.wav` (full) | ✅ `000.wav` |

Chunked endpoint (`path` variations, name `000.wav`):

| `path` | result |
|---|---|
| `ivr2:zztest/` (dir) | ✅ `000.wav` |
| `ivr2:zztest` (dir) | ✅ `000.wav` |
| `ivr2:zztest/000.wav` (full) | ❌ nested `000.wav/000.wav` |

Chunked + **valid audio** + `autoNumbering=False`:

| name | result |
|---|---|
| `000.wav` | ❌ `zztest/000/000.wav` (creates sub-extension `000/`) |
| `song.wav` | ❌ `zztest/song/000.wav` |

> Nesting happens in **plain folders too** — not menu-specific. Non-audio/garbage
> bytes land flat; valid audio triggers the server's message-finalizer. This is a
> **Yemot platform behavior**, the website does the same.

Chunked + `autoNumbering=True`:

| upload | result |
|---|---|
| 1st | ✅ `000.wav` |
| 2nd | ✅ `001.wav` |

Simple endpoint size limit: 60 MB ✅, 70 MB ❌ (non-JSON / connection reset) → **~64 MB**.

`file_name` must include the **extension** — a bare `000` is treated as a sub-folder
(`677/000/000.wav`).

## 3. Root cause

1. The library sent the **full** `path` (`ivr2:677/000.wav`) to **both** protocols.
   The chunked endpoint treats `path` as a directory and appends `qqfilename`
   → `677/000.wav` + `000` + convert → `677/000.wav/000/000.wav` (the nesting).
2. The chunked `?done` response was **not checked** for `success` → an `ERROR`
   response went straight into `types.UploadFile(**response)` → pydantic
   `ValidationError` crash instead of a clean `YemotAPIError`.

## 4. Changes made

Files: `src/yemot_api/yemot_api.py`, `src/yemot_api/async_yemot_api.py`.

- **Unified public convention**: `path` = target **folder**, `file_name` = **filename**
  (matches the website + the existence of a separate `file_name` param).
  `upload_file` computes `folder = f"{base_path}{path}".rstrip("/")` once, then:
  - **simple** → `data["path"] = f"{folder}/{file_name}"` (full path it requires)
  - **chunked** → `path = f"{folder}/"`, `qqfilename = file_name`
- **`?done` error handling**: `self._check_response(response)` before constructing
  `UploadFile` → raises `YemotAPIError` on server `ERROR`.
- `base_path` is **unchanged** as a public parameter (default `"ivr2:"`); it is just
  folded into `folder` before dispatch. Removed only from the private helper
  signatures.

## 5. ⚠ Breaking-change analysis

The public contract of `upload_file` changed.

| caller pattern | old (small) | new (small) | impact |
|---|---|---|---|
| `path="677/000.wav"`, `file_name="000"` | → `ivr2:677/000.wav` ✅ | → `ivr2:677/000.wav/000` | **BREAKS** |
| `path="677"`, `file_name="000.wav"` | → `ivr2:677` → `"path is invalid"` ❌ | → `ivr2:677/000.wav` ✅ | fixed |
| large file (any) | nested / crash | consistent path handling | improved |

- Callers who put the **filename inside `path`** are broken → must switch to
  `path`=folder + `file_name`=name (with extension).
- Large-file callers were already broken, so no working usage is lost there.

Recommendation: treat as a breaking change — **bump the version** and note it in the
changelog.

## 6. Decisions (per maintainer, 2026-06-24)

- Keep the **49 MB** chunk threshold (not raised to ~60 MB).
- Do **not** auto-flatten chunked nesting (no post-upload move workaround).

## 7. Usage guidance

```python
# small file (< ~64 MB): exact flat placement
ins.upload_file(path="677", blob=content, file_name="000.wav",
                convert_audio=True, auto_numbering=False)
# -> ivr2:677/000.wav

# large file (> ~64 MB, must chunk): flat placement requires auto-numbering
ins.upload_file(path="677", blob=content, file_name="000.wav",
                convert_audio=True, auto_numbering=True)
# -> ivr2:677/000.wav  (next free message number)

# large file + auto_numbering=False  -> nests to 677/000/000.wav (Yemot behavior)
```

Rules:
- `file_name` **must** include the extension (`000.wav`, not `000`).
- For large audio that must land as a flat named message, use `auto_numbering=True`.
