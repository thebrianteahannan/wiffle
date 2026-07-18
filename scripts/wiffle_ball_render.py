#!/usr/bin/env python3
"""Realistic shaded Wiffle ball renderer (8 recessed oblong holes)."""

from __future__ import annotations

import math

import numpy as np
from PIL import Image, ImageDraw

# Spaced 2×4 grid on the hole face (degrees from face center).
HOLE_LOCS = [
    (-26, -54),
    (26, -54),
    (-26, -18),
    (26, -18),
    (-26, 18),
    (26, 18),
    (-26, 54),
    (26, 54),
]


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
    pts = []
    for lon, lat in HOLE_LOCS:
        lo, la = math.radians(lon), math.radians(lat)
        pts.append(
            np.array(
                [
                    math.cos(la) * math.sin(lo),
                    math.sin(la),
                    math.cos(la) * math.cos(lo),
                ],
                dtype=np.float64,
            )
        )
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
) -> None:
    """
    Paint a plastic Wiffle ball with 8 distinct recessed oblong holes.

    holes_angle_deg: hole-hemisphere direction on screen (0=right, 90=up, 180=left, 270=down).
    face_camera: 0 = equator/side view; 1 = hole face pointed at camera.
    holes_away: if True, smooth half faces camera.
    """
    pitch = 90.0 * (1.0 - face_camera) + (180.0 if holes_away else 0.0)
    centers = [
        np.array(_rot_z(_rot_y(tuple(c), pitch), holes_angle_deg), dtype=np.float64)
        for c in _hole_centers_model()
    ]
    face_axis = np.array(
        _rot_z(_rot_y((0.0, 0.0, 1.0), pitch), holes_angle_deg), dtype=np.float64
    )

    half_long = math.radians(10.8)
    half_short = math.radians(4.6)

    size = 2 * r + 2
    xs = np.arange(size) - r
    ys = np.arange(size) - r
    xx, yy = np.meshgrid(xs, ys)
    rr2 = xx * xx + yy * yy
    rad = float(r - 0.9)
    mask = rr2 <= rad * rad
    zz = np.zeros_like(xx, dtype=np.float64)
    zz[mask] = np.sqrt(np.maximum(rad * rad - rr2[mask], 0.0))

    # Outer surface points in pixel units (camera along +Z)
    p = np.zeros((size, size, 3), dtype=np.float64)
    p[..., 0][mask] = xx[mask]
    p[..., 1][mask] = -yy[mask]
    p[..., 2][mask] = zz[mask]
    n = p / r

    light = np.array([-0.28, 0.42, 0.86], dtype=np.float64)
    light /= np.linalg.norm(light)
    ndotl = np.clip((n * light).sum(-1), 0, 1)

    base = np.array([253.0, 225.0, 56.0])
    rgb = base * (0.64 + 0.32 * ndotl[..., None])
    rgb += (30.0 * (ndotl ** 14))[..., None]
    rgb *= (1.0 - 0.15 * np.clip(rr2 / (r * r), 0, 1) ** 1.45)[..., None]

    if show_seam:
        seam_d = np.abs((n * face_axis).sum(-1))
        seam = mask & (seam_d < 0.028)
        rgb[seam] = rgb[seam] * 0.5 + np.array([140.0, 118.0, 38.0]) * 0.5

    best = np.full((size, size), 1e9, dtype=np.float64)
    for c in centers:
        up = np.array([0.0, 1.0, 0.0])
        long_ax = up - c * np.dot(up, c)
        if np.linalg.norm(long_ax) < 1e-6:
            long_ax = np.array([1.0, 0.0, 0.0]) - c * c[0]
        long_ax /= np.linalg.norm(long_ax)
        short_ax = np.cross(c, long_ax)
        short_ax /= max(np.linalg.norm(short_ax), 1e-9)
        d_long = (n * long_ax).sum(-1)
        d_short = (n * short_ax).sum(-1)
        d_face = (n * c).sum(-1)
        dist = _capsule_dist(d_long, d_short, half_long, half_short)
        use = mask & (d_face > 0.18) & (dist < best)
        best = np.where(use, dist, best)

    ao_w = math.radians(2.4)
    rim_w = math.radians(0.7)
    in_hole = mask & (best <= 0.0)
    ao_ring = mask & (best > 0.0) & (best <= ao_w)
    thin_rim = mask & (best > 0.0) & (best <= rim_w)

    if ao_ring.any():
        ao = np.clip(1.0 - best / ao_w, 0, 1)
        rgb[ao_ring] *= (1.0 - 0.40 * ao[ao_ring])[..., None]
    rgb[thin_rim] = 0.4 * rgb[thin_rim] + 0.6 * np.array([255.0, 242.0, 160.0])

    # True hollow look: rays through openings hit the inner back shell
    if in_hole.any():
        # Camera at z = +infinity (orthographic): ray dir = (0,0,-1)
        # Point on outer sphere p; continue inward along -Z and find second
        # intersection with inner sphere of radius r_in.
        r_in = 0.90 * rad
        # Ray: o + t*d with d=(0,0,-1), o = p (on outer). For ortho from +Z,
        # march in -Z: x,y fixed, z decreases.
        # Inner sphere: x^2+y^2+z^2 = r_in^2
        x = p[..., 0]
        y = p[..., 1]
        rho2 = x * x + y * y
        # Valid if rho2 <= r_in^2
        can_hit = in_hole & (rho2 <= r_in * r_in)
        z_back = -np.sqrt(np.maximum(r_in * r_in - rho2, 0.0))
        # Shade back wall with simple lighting using inward/outward normal
        back_n = np.zeros_like(p)
        back_n[..., 0][can_hit] = x[can_hit] / r_in
        back_n[..., 1][can_hit] = y[can_hit] / r_in
        back_n[..., 2][can_hit] = z_back[can_hit] / r_in
        # Inside of shell: flip normal to face inward (toward cavity center-ish)
        # For viewing, use lit inward surface
        bn_dot = np.clip((-back_n * light).sum(-1), 0.05, 1)
        back_col = np.array([55.0, 48.0, 28.0]) * (0.45 + 0.55 * bn_dot[..., None])
        # Near the hole rim, darken (tunnel)
        tunnel = np.clip(-best / half_short, 0, 1)
        back_col = back_col * (0.55 + 0.45 * (1.0 - tunnel[..., None]))

        rgb[can_hit] = back_col[can_hit]
        # Openings that don't hit back wall (near limb): deep black void
        void = in_hole & ~can_hit
        rgb[void] = np.array([12.0, 14.0, 18.0])

        # Inner plastic lip (shell thickness) just inside the outline
        inner = in_hole & (best > -rim_w * 2.5)
        rgb[inner] = 0.35 * rgb[inner] + 0.65 * np.array([95.0, 82.0, 30.0])

    out = np.zeros((size, size, 3), dtype=np.uint8)
    out[mask] = np.clip(rgb[mask], 0, 255).astype(np.uint8)
    ball = Image.fromarray(out, "RGB")
    alpha = Image.new("L", (size, size), 0)
    ImageDraw.Draw(alpha).ellipse((1, 1, size - 2, size - 2), fill=255)
    img.paste(ball, (int(cx - r), int(cy - r)), alpha)
    ImageDraw.Draw(img).ellipse(
        (cx - r, cy - r, cx + r, cy + r),
        outline=(135, 110, 28),
        width=max(2, r // 45),
    )
