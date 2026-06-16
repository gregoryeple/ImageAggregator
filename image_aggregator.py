from pathlib import Path
from PIL import Image
from enum import Enum

# Enum
class SortMode(Enum):
    ALPHABETICAL = "alphabetical"
    CREATION_TIME = "creation_time"
    MODIFICATION_TIME = "modification_time"

class Direction(Enum):
    HORIZONTAL = "horizontal"
    VERTICAL = "vertical"

class Alignment(Enum):
    START = "start"
    CENTER = "center"
    END = "end"

# Constants
DATA_FOLDER = "input"
OUTPUT_IMAGE = "output/aggregate.png"
SORT_MODE = SortMode.ALPHABETICAL
REVERSE_ORDER = False
FUSION_DIRECTION = Direction.VERTICAL
IMAGE_ALIGNMENT = Alignment.CENTER
BACKGROUND_COLOR = "#00000000" # Format #RRGGBB[AA]
SUPPORTED_EXTENSIONS = {
    ".png",
    ".jpg",
    ".jpeg",
    ".bmp",
    ".gif",
    ".webp",
    ".tiff",
}

# Utilities
def parse_color(color: str):
    color = color.strip().lstrip("#")
    if len(color) == 6:
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        a = 255
        return r, g, b, a
    if len(color) == 8:
        r = int(color[0:2], 16)
        g = int(color[2:4], 16)
        b = int(color[4:6], 16)
        a = int(color[6:8], 16)
        return r, g, b, a
    raise ValueError("BACKGROUND_COLOR must be '#RRGGBB' or '#RRGGBBAA'")

def get_sorted_images(folder: Path):
    images = [file for file in folder.iterdir() if file.is_file() and file.suffix.lower() in SUPPORTED_EXTENSIONS]
    if SORT_MODE == SortMode.ALPHABETICAL:
        images.sort(key=lambda p: p.name.lower())
    elif SORT_MODE == SortMode.CREATION_TIME:
        images.sort(key=lambda p: p.stat().st_ctime)
    elif SORT_MODE == SortMode.MODIFICATION_TIME:
        images.sort(key=lambda p: p.stat().st_mtime)
    if REVERSE_ORDER:
        images.reverse()
    return images

# Main

def main():
    data_folder = Path(DATA_FOLDER)
    if not data_folder.exists():
        raise FileNotFoundError(f"Folder does not exist: {data_folder}")
    image_paths = get_sorted_images(data_folder)
    if not image_paths:
        raise RuntimeError(f"No supported images found in '{DATA_FOLDER}'")
    images = [Image.open(path).convert("RGBA") for path in image_paths]
    if FUSION_DIRECTION == Direction.VERTICAL:
        output_width = max(img.width for img in images)
        output_height = sum(img.height for img in images)
        canvas = Image.new("RGBA", (output_width, output_height), parse_color(BACKGROUND_COLOR))
        y = 0
        for img in images:
            if IMAGE_ALIGNMENT == Alignment.START:
                x = 0
            elif IMAGE_ALIGNMENT == Alignment.CENTER:
                x = (output_width - img.width) // 2
            else: # Alignment.END
                x = output_width - img.width
            canvas.paste(img, (x, y), img)
            y += img.height
    else:  # HORIZONTAL
        output_width = sum(img.width for img in images)
        output_height = max(img.height for img in images)
        canvas = Image.new("RGBA", (output_width, output_height), parse_color(BACKGROUND_COLOR))
        x = 0
        for img in images:
            if IMAGE_ALIGNMENT == Alignment.START:
                y = 0
            elif IMAGE_ALIGNMENT == Alignment.CENTER:
                y = (output_height - img.height) // 2
            else: # Alignment.END
                y = output_height - img.height
            canvas.paste(img, (x, y), img)
            x += img.width
    output_path = Path(OUTPUT_IMAGE)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    canvas.save(output_path)
    print(f"Created: {output_path}")
    print(f"Images used: {len(images)}")
    print(f"Final size: {canvas.width}x{canvas.height}")

if __name__ == "__main__":
    main()