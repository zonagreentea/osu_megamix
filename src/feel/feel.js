/**
 * FEEL 1.0 — Fixed Electronic Electron Lendering
 * Native-resolution, aspect-preserving Canvas 2D rendering.
 * No external dependencies.
 */
(function (global) {
  "use strict";

  const MIN_SCALE = 0.25;
  const MAX_SCALE = 4;

  function clampScale(scale) {
    if (!Number.isFinite(scale)) {
      throw new TypeError("FEEL: scale must be finite");
    }
    return Math.max(MIN_SCALE, Math.min(MAX_SCALE, scale));
  }

  function dimensions(width, height, scale = 1) {
    if (![width, height].every(
      n => Number.isFinite(n) && n >= 0
    )) {
      throw new RangeError("FEEL: invalid dimensions");
    }

    const s = clampScale(scale);

    return {
      width: width * s,
      height: height * s,
      scale: s
    };
  }

  function draw(ctx, image, x, y, scale = 1) {
    if (!ctx || typeof ctx.drawImage !== "function") {
      throw new TypeError("FEEL: Canvas 2D context required");
    }

    const width = image.naturalWidth ?? image.width;
    const height = image.naturalHeight ?? image.height;

    if (!width || !height) {
      throw new RangeError("FEEL: image has no dimensions");
    }

    const size = dimensions(width, height, scale);

    ctx.drawImage(
      image,
      x,
      y,
      size.width,
      size.height
    );

    return size;
  }

  function fit(width, height, maxWidth, maxHeight) {
    if (width <= 0 || height <= 0 ||
        maxWidth <= 0 || maxHeight <= 0) {
      throw new RangeError("FEEL: dimensions must be positive");
    }

    return clampScale(
      Math.min(maxWidth / width, maxHeight / height)
    );
  }

  global.FEEL = Object.freeze({
    version: "1.0.0",
    MIN_SCALE,
    MAX_SCALE,
    clampScale,
    dimensions,
    draw,
    fit
  });
})(globalThis);
