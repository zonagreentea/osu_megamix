def image_to_ascii(path, width=80):
    chars = "@%#*+=-:. "

    with open(path, "rb") as f:
        data = f.read()

    # For real image decoding, Python's standard library alone
    # doesn't provide a general PNG/JPEG decoder.