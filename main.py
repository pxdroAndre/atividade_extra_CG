import os
import sys
import numpy as np
from PIL import Image
# Force GLX on Wayland/Xwayland when not specified to avoid context errors.
if "PYOPENGL_PLATFORM" not in os.environ:
    os.environ["PYOPENGL_PLATFORM"] = "glx"

from OpenGL.GL import (
    glClear,
    glClearColor,
    glDrawPixels,
    glPixelStorei,
    glPixelZoom,
    glRasterPos2f,
    glViewport,
    GL_COLOR_BUFFER_BIT,
    GL_RGB,
    GL_UNSIGNED_BYTE,
    GL_UNPACK_ALIGNMENT,
)
from OpenGL.GLUT import (
    glutInit,
    glutInitDisplayMode,
    glutInitWindowSize,
    glutCreateWindow,
    glutDisplayFunc,
    glutReshapeFunc,
    glutKeyboardFunc,
    glutSwapBuffers,
    glutMainLoop,
    glutPostRedisplay,
    GLUT_DOUBLE,
    GLUT_RGB,
)

# Tkinter is used only for file dialogs (keeps UI minimal).
try:
    import tkinter as tk
    from tkinter import filedialog
except Exception as exc:
    print("Tkinter not available:", exc)
    sys.exit(1)


WINDOW_W = 960
WINDOW_H = 720

image_rgb = None
image_hsv = None
image_hsv_viz = None
image_path = None
view_mode = "rgb"  # rgb | hsv_viz | hsv_raw


def rgb_to_hsv_image(rgb_uint8):
    """Convert an RGB uint8 image to HSV uint8 using the classic sector formula."""
    rgb = rgb_uint8.astype(np.float32) / 255.0
    r = rgb[..., 0]
    g = rgb[..., 1]
    b = rgb[..., 2]

    maxc = np.maximum(np.maximum(r, g), b)
    minc = np.minimum(np.minimum(r, g), b)
    delta = maxc - minc

    h = np.zeros_like(maxc)
    mask = delta > 0.0

    mask_r = (maxc == r) & mask
    mask_g = (maxc == g) & mask
    mask_b = (maxc == b) & mask

    r_div = np.zeros_like(delta)
    g_div = np.zeros_like(delta)
    b_div = np.zeros_like(delta)
    np.divide(g - b, delta, out=r_div, where=mask_r)
    np.divide(b - r, delta, out=g_div, where=mask_g)
    np.divide(r - g, delta, out=b_div, where=mask_b)

    h[mask_r] = r_div[mask_r] % 6.0
    h[mask_g] = g_div[mask_g] + 2.0
    h[mask_b] = b_div[mask_b] + 4.0

    h = h / 6.0
    s = np.where(maxc == 0.0, 0.0, delta / maxc)
    v = maxc

    hsv = np.stack([h, s, v], axis=2)
    hsv_uint8 = np.clip(hsv * 255.0, 0, 255).astype(np.uint8)
    return hsv_uint8


def hsv_to_rgb_image(hsv_uint8):
    """Convert HSV uint8 (H,S,V in [0..255]) to RGB uint8 for display."""
    hsv = hsv_uint8.astype(np.float32) / 255.0
    h = hsv[..., 0] * 6.0
    s = hsv[..., 1]
    v = hsv[..., 2]

    i = np.floor(h).astype(np.int32) % 6
    f = h - np.floor(h)

    p = v * (1.0 - s)
    q = v * (1.0 - s * f)
    t = v * (1.0 - s * (1.0 - f))

    r = np.zeros_like(v)
    g = np.zeros_like(v)
    b = np.zeros_like(v)

    m0 = i == 0
    m1 = i == 1
    m2 = i == 2
    m3 = i == 3
    m4 = i == 4
    m5 = i == 5

    r[m0], g[m0], b[m0] = v[m0], t[m0], p[m0]
    r[m1], g[m1], b[m1] = q[m1], v[m1], p[m1]
    r[m2], g[m2], b[m2] = p[m2], v[m2], t[m2]
    r[m3], g[m3], b[m3] = p[m3], q[m3], v[m3]
    r[m4], g[m4], b[m4] = t[m4], p[m4], v[m4]
    r[m5], g[m5], b[m5] = v[m5], p[m5], q[m5]

    rgb = np.stack([r, g, b], axis=2)
    return np.clip(rgb * 255.0, 0, 255).astype(np.uint8)


def open_image_dialog():
    global image_rgb, image_hsv, image_hsv_viz, image_path
    root = tk.Tk()
    root.withdraw()
    path = filedialog.askopenfilename(
        title="Select an image",
        filetypes=[("Image files", "*.png;*.jpg;*.jpeg;*.bmp;*.tif;*.tiff")],
    )
    root.destroy()
    if not path:
        return

    image_path = path
    img = Image.open(path).convert("RGB")
    image_rgb = np.array(img, dtype=np.uint8)
    image_hsv = rgb_to_hsv_image(image_rgb)
    image_hsv_viz = hsv_to_rgb_image(image_hsv)


def save_hsv_dialog():
    if image_hsv is None:
        return
    root = tk.Tk()
    root.withdraw()
    path = filedialog.asksaveasfilename(
        title="Save HSV image",
        defaultextension=".png",
        filetypes=[("PNG", "*.png"), ("JPEG", "*.jpg;*.jpeg"), ("BMP", "*.bmp")],
    )
    root.destroy()
    if not path:
        return

    Image.fromarray(image_hsv, mode="RGB").save(path)


def get_display_image():
    if image_rgb is None:
        return None
    if view_mode == "hsv_raw":
        return image_hsv
    if view_mode == "hsv_viz":
        return image_hsv_viz
    return image_rgb


def display():
    glClear(GL_COLOR_BUFFER_BIT)

    img = get_display_image()
    if img is None:
        glutSwapBuffers()
        glutPostRedisplay()
        return

    # Flip vertically to match OpenGL's origin at bottom-left.
    img_flipped = np.flipud(img)
    height, width = img_flipped.shape[:2]

    # Fit image to the window while preserving aspect ratio.
    scale_x = WINDOW_W / float(width)
    scale_y = WINDOW_H / float(height)
    scale = min(scale_x, scale_y)

    draw_w = int(width * scale)
    draw_h = int(height * scale)
    offset_x = (WINDOW_W - draw_w) // 2
    offset_y = (WINDOW_H - draw_h) // 2

    glRasterPos2f(-1.0 + 2.0 * offset_x / WINDOW_W, -1.0 + 2.0 * offset_y / WINDOW_H)
    glPixelZoom(scale, scale)
    glPixelStorei(GL_UNPACK_ALIGNMENT, 1)
    glDrawPixels(width, height, GL_RGB, GL_UNSIGNED_BYTE, img_flipped)

    glutSwapBuffers()
    glutPostRedisplay()


def reshape(width, height):
    global WINDOW_W, WINDOW_H
    WINDOW_W = max(1, width)
    WINDOW_H = max(1, height)
    glViewport(0, 0, WINDOW_W, WINDOW_H)


def keyboard(key, _x, _y):
    global view_mode
    if key in (b"q", b"\x1b"):
        sys.exit(0)
    if key == b"o":
        open_image_dialog()
    elif key == b"1":
        view_mode = "rgb"
    elif key == b"2":
        view_mode = "hsv_viz"
    elif key == b"3":
        view_mode = "hsv_raw"
    elif key == b"s":
        save_hsv_dialog()


def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(WINDOW_W, WINDOW_H)
    glutCreateWindow(b"RGB -> HSV Viewer")

    glClearColor(0.08, 0.08, 0.08, 1.0)

    glutDisplayFunc(display)
    glutReshapeFunc(reshape)
    glutKeyboardFunc(keyboard)

    print("Controls:")
    print("  o: open image")
    print("  1: view RGB")
    print("  2: view HSV converted back to RGB (natural colors)")
    print("  3: view HSV raw channels (false colors)")
    print("  s: save HSV image")
    print("  q or Esc: quit")

    glutMainLoop()


if __name__ == "__main__":
    main()
