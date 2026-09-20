#!/usr/bin/env python3
"""Realistic official-style Wiffle ball renderer.

Eight oblong slots on ONE hemisphere, arranged in a ring around the face
pole, each elongated toward that pole (spoke / radial pattern) — matching
real Wiffle balls, not a parallel 2×4 grid.
"""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw

# Angular distance of each slot center from the hole-face pole (degrees).
HOLE_COLAT_DEG = 36.0
# Half-size of each stadium slot (degrees along long/short axes).
HALF_LONG_DEG = 11.5
HALF_SHORT_DEG = 4.4


def _rot_y(v, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    x, y, z = v
    return (c * x + s * z, y, -s * x + c * z)


def _rot_z(v, deg):
    a = math.radians(deg)
    c, s = math.cos(a), math.sin(a)
    x, y, z = v
    return (c * x - s * y, s * x + c * y, z)


def _hole_centers_model():
    """8 slot centers in a ring around +Z (hole-face pole)."""
    colat = math.radians(HOLE_COLAT_DEG)
    pts = []
    for i in range(8):
        az = math.radians(i * 45.0)
        # +Z = pole of perforated face; ring in x–y
        x = math.sin(colat) * math.cos(az)
        y = math.sin(colat) * math.sin(az)
        z = math.cos(colat)
        pts.append(np.array([x, y, z], dtype=np.float64))
    return pts


def _capsule_dist(d_long, d_short, half_long, half_short):
    straight = max(half_long - half_short, 0.0)
    ax = np.abs(d_long) - straight
    return np.where(
        ax > 0,
        np.sqrt(ax * ax + d_short * d_short) - half_short,
        np.abs(d_short) - half_short,
    )


def render_wiffle_ball(
    img: Image.Image,
    cx: int,
    cy: int,
    r: int,
    holes_angle_deg: float = 0,
    *,
    face_camera: float = 0.0,
    show_seam: bool = True,
    holes_away: bool = False,
    color: str = "white",
) -> None:
    """
    Paint a hollow plastic Wiffle ball with 8 radial oblong slots.

    holes_angle_deg: where the hole-face pole points on screen
      (0=right, 90=up, 180=left, 270=down).
    face_camera: 0 = equator/side view; 1 = hole face pointed at camera.
    holes_away: smooth half toward camera.
    color: "white" (official look) or "yellow".
    """
    pitch = 90.0 * (1.0 - face_camera) + (180.0 if holes_away else 0.0)

    def xform(v):
        return np.array(_rot_z(_rot_y(tuple(v), pitch), holes_angle_deg), dtype=np.float64)

    pole = xform((0.0, 0.0, 1.0))  # hole-face pole after rotation
    centers = [xform(tuple(c)) for c in _hole_centers_model()]

    half_long = math.radians(HALF_LONG_DEG)
    half_short = math.radians(HALF_SHORT_DEG)

    size = 2 * r + 2
    xs = np.arange(size) - r
    ys = np.arange(size) - r
    xx, yy = np.meshgrid(xs, ys)
    rr2 = xx * xx + yy * yy
    rad = float(r - 0.9)
    mask = rr2 <= rad * rad
    zz = np.zeros_like(xx, dtype=np.float64)
    zz[mask] = np.sqrt(np.maximum(rad * rad - rr2[mask], 0.0))

    p = np.zeros((size, size, 3), dtype=np.float64)
    p[..., 0][mask] = xx[mask]
    p[..., 1][mask] = -yy[mask]
    p[..., 2][mask] = zz[mask]
    n = p / r

    light = np.array([-0.35, 0.5, 0.79], dtype=np.float64)
    light /= np.linalg.norm(light)
    ndotl = np.clip((n * light).sum(-1), 0, 1)
    view = np.array([0.08, 0.12, 1.0], dtype=np.float64)
    view /= np.linalg.norm(view)
    halfv = light + view
    halfv /= np.linalg.norm(halfv)
    spec = np.clip((n * halfv).sum(-1), 0, 1) ** 45

    if color == "yellow":
        base = np.array([252.0, 220.0, 55.0])
    else:
        # Official-style off-white plastic
        base = np.array([244.0, 244.0, 240.0])

    rgb = base * (0.58 + 0.38 * ndotl[..., None])
    rgb += ((55.0 if color == "white" else 36.0) * spec)[..., None]
    # Soft limb darkening
    limb = np.clip(rr2 / (r * r), 0, 1) ** 1.35
    rgb *= (1.0 - 0.18 * limb)[..., None]

    # Faint latitudinal mold / parting lines (real balls show these)
    # Use angle around an axis perpendicular to face pole
    # Project onto plane ⊥ pole
    # Simple: banded by world Y before... use angle from equator of face
    face_lat = (n * pole).sum(-1)
    bands = np.sin(face_lat * 28.0) ** 2
    mold = mask & (bands > 0.92) & (np.abs(face_lat) < 0.85)
    rgb[mold] = rgb[mold] * 0.93

    if show_seam:
        # Equator between holed half and smooth half
        seam_d = np.abs((n * pole).sum(-1))
        seam = mask & (seam_d < 0.025)
        ridge = mask & (seam_d >= 0.025) & (seam_d < 0.05)
        seam_col = np.array([200.0, 200.0, 195.0]) if color == "white" else np.array([150.0, 125.0, 40.0])
        rgb[seam] = rgb[seam] * 0.55 + seam_col * 0.45
        rgb[ridge] = rgb[ridge] * 0.94 + np.array([255.0, 255.0, 250.0]) * 0.06

    # Slot distance field — long axis RADIAL from hole-face pole (spoke pattern)
    best = np.full((size, size), 1e9, dtype=np.float64)
    for c in centers:
        # Meridian / spoke direction on the sphere at c (away from pole along surface)
        # long_ax ⊥ c, in the plane of (pole, c)
        long_ax = pole - c * np.dot(pole, c)
        if np.linalg.norm(long_ax) < 1e-8:
            long_ax = np.array([0.0, 1.0, 0.0]) - c * c[1]
        long_ax /= np.linalg.norm(long_ax)
        short_ax = np.cross(c, long_ax)
        short_ax /= max(np.linalg.norm(short_ax), 1e-9)

        d_long = (n * long_ax).sum(-1)
        d_short = (n * short_ax).sum(-1)
        d_face = (n * c).sum(-1)
        dist = _capsule_dist(d_long, d_short, half_long, half_short)
        use = mask & (d_face > 0.15) & (dist < best)
        best = np.where(use, dist, best)

    ao_w = math.radians(2.6)
    rim_w = math.radians(0.75)
    in_hole = mask & (best <= 0.0)
    ao_ring = mask & (best > 0.0) & (best <= ao_w)
    thin_rim = mask & (best > 0.0) & (best <= rim_w)

    if ao_ring.any():
        ao = np.clip(1.0 - best / ao_w, 0, 1)
        rgb[ao_ring] *= (1.0 - 0.42 * ao[ao_ring])[..., None]

    # Cut-edge highlight (shell thickness)
    rim_col = np.array([255.0, 255.0, 250.0]) if color == "white" else np.array([255.0, 242.0, 160.0])
    rgb[thin_rim] = 0.3 * rgb[thin_rim] + 0.7 * rim_col

    # Hollow interior: see the back inner wall through each slot
    if in_hole.any():
        r_in = 0.905 * rad
        x = p[..., 0]
        y = p[..., 1]
        rho2 = x * x + y * y
        can_hit = in_hole & (rho2 <= r_in * r_in)
        z_back = -np.sqrt(np.maximum(r_in * r_in - rho2, 0.0))
        back_n = np.zeros_like(p)
        back_n[..., 0][can_hit] = x[can_hit] / r_in
        back_n[..., 1][can_hit] = y[can_hit] / r_in
        back_n[..., 2][can_hit] = z_back[can_hit] / r_in
        bn_dot = np.clip((-back_n * light).sum(-1), 0.04, 1)
        # Warm dark plastic inside
        if color == "white":
            back_base = np.array([48.0, 48.0, 50.0])
        else:
            back_base = np.array([55.0, 48.0, 28.0])
        back_col = back_base * (0.4 + 0.6 * bn_dot[..., None])
        tunnel = np.clip(-best / half_short, 0, 1)
        back_col = back_col * (0.5 + 0.5 * (1.0 - tunnel[..., None]))
        rgb[can_hit] = back_col[can_hit]
        rgb[in_hole & ~can_hit] = np.array([10.0, 11.0, 14.0])

        inner = in_hole & (best > -rim_w * 2.4)
        wall = np.array([170.0, 170.0, 168.0]) if color == "white" else np.array([95.0, 82.0, 30.0])
        rgb[inner] = 0.4 * rgb[inner] + 0.6 * wall

    out = np.zeros((size, size, 3), dtype=np.uint8)
    out[mask] = np.clip(rgb[mask], 0, 255).astype(np.uint8)
    ball = Image.fromarray(out, "RGB")
    alpha = Image.new("L", (size, size), 0)
    ImageDraw.Draw(alpha).ellipse((1, 1, size - 2, size - 2), fill=255)
    img.paste(ball, (int(cx - r), int(cy - r)), alpha)
    outline = (170, 170, 165) if color == "white" else (135, 110, 28)
    ImageDraw.Draw(img).ellipse((cx - r, cy - r, cx + r, cy + r), outline=outline, width=max(2, r // 48))
