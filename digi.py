from PIL import Image, ImageDraw
import os
import csv
import random

OUTPUT_DIR = "digital_dataset"
CSV_FILE = "clock_times.csv"
os.makedirs(OUTPUT_DIR, exist_ok=True)

digits = {
    "0": [1,1,1,1,1,1,0],
    "1": [0,1,1,0,0,0,0],
    "2": [1,1,0,1,1,0,1],
    "3": [1,1,1,1,0,0,1],
    "4": [0,1,1,0,0,1,1],
    "5": [1,0,1,1,0,1,1],
    "6": [1,0,1,1,1,1,1],
    "7": [1,1,1,0,0,0,0],
    "8": [1,1,1,1,1,1,1],
    "9": [1,1,1,1,0,1,1],
}

# =========================
# DRAW DIGIT
# =========================
def draw_digit(draw, x, y, size, digit, on_color, off_color):
    seg = digits[digit]

    W = size
    H = size * 2
    t = max(int(size * 0.18), 2)

    segments = [
        (x+t, y, x+W-t, y+t),
        (x+W-t, y+t, x+W, y+H/2 - t/2),
        (x+W-t, y+H/2 + t/2, x+W, y+H-t),
        (x+t, y+H-t, x+W-t, y+H),
        (x, y+H/2 + t/2, x+t, y+H-t),
        (x, y+t, x+t, y+H/2 - t/2),
        (x+t, y+H/2 - t/2, x+W-t, y+H/2 + t/2),
    ]

    for i, rect in enumerate(segments):
        draw.rectangle(rect, fill=on_color if seg[i] else off_color)

# =========================
# DRAW CLOCK WITH DESIGN
# =========================
def draw_digital(h, m, s, idx, design):
    img_w, img_h = 1000, 300
    img = Image.new("RGB", (img_w, img_h), design["bg_color"])
    draw = ImageDraw.Draw(img)

    time_str = f"{h:02d}{m:02d}{s:02d}"
    size = design["size"]
    digit_w = size
    colon_w = design["colon_width"]
    digit_gap = design["digit_gap"]
    colon_gap = design["colon_gap"]

    layout = []
    for i, d in enumerate(time_str):
        layout.append(("digit", d))
        if i == 1 or i == 3:
            layout.append(("colon", ":"))

    total_width = 0
    for item in layout:
        total_width += digit_w + digit_gap if item[0] == "digit" else colon_w + colon_gap
    total_width -= digit_gap

    start_x = (img_w - total_width) // 2
    y = (img_h - size*2) // 2
    x = start_x

    for item in layout:
        if item[0] == "digit":
            draw_digit(draw, x, y, size, item[1], design["segment_on"], design["segment_off"])
            x += digit_w + digit_gap
        else:
            cx = x + colon_gap // 2
            r = design["colon_radius"]
            draw.ellipse((cx, y + size*0.6, cx+r, y + size*0.6 + r), fill=design["segment_on"])
            draw.ellipse((cx, y + size*1.3, cx+r, y + size*1.3 + r), fill=design["segment_on"])
            x += colon_w + colon_gap

    if design["border"]:
        border_width = design["border_width"]
        draw.rectangle(
            [border_width//2, border_width//2, img_w-border_width//2-1, img_h-border_width//2-1],
            outline=design["border_color"],
            width=border_width
        )

    path = os.path.join(OUTPUT_DIR, f"digital_{idx:05d}.png")
    img.save(path)
    return path



# TEST


def random_color(min_val=0, max_val=255):
    return (random.randint(min_val, max_val), random.randint(min_val, max_val), random.randint(min_val, max_val))


def generate_designs(num_designs=10):
    designs = []
    for design_id in range(num_designs):
        bg_color = random_color(0, 255)
        segment_on = random_color(150, 255)
        segment_off = random_color(0, 80)
        designs.append({
            "design_id": design_id,
            "bg_color": bg_color,
            "segment_on": segment_on,
            "segment_off": segment_off,
            "size": random.randint(60, 90),
            "digit_gap": random.randint(20, 45),
            "colon_gap": random.randint(30, 75),
            "colon_width": random.randint(10, 20),
            "colon_radius": random.randint(10, 16),
            "border": random.choice([True, False]),
            "border_color": random_color(100, 255),
            "border_width": random.randint(2, 10)
        })
    return designs


def generate_dataset(num_designs=10, times_per_design=300):
    designs = generate_designs(num_designs)
    all_times = [(h, m, s) for h in range(24) for m in range(60) for s in range(60)]
    random.shuffle(all_times)

    fieldnames = [
        "sample_id", "design_id", "filename", "hour", "minute", "second", "time_string"
    ]

    existing_rows = 0
    if os.path.exists(CSV_FILE):
        with open(CSV_FILE, "r", newline="") as csvfile:
            reader = csv.DictReader(csvfile)
            existing_rows = list(reader)

        if existing_rows:
            existing_rows = [
                {key: row[key] for key in fieldnames if key in row}
                for row in existing_rows
            ]
            if reader.fieldnames != fieldnames:
                with open(CSV_FILE, "w", newline="") as csvfile:
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    writer.writeheader()
                    writer.writerows(existing_rows)
                existing_rows = len(existing_rows)
            else:
                existing_rows = len(existing_rows)
        else:
            existing_rows = 0

    write_header = existing_rows == 0
    open_mode = "a" if existing_rows else "w"
    with open(CSV_FILE, open_mode, newline="") as csvfile:
        writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
        if write_header:
            writer.writeheader()

        sample_id = existing_rows
        time_index = 0
        for design in designs:
            print(f"Generating design {design['design_id'] + 1}/{num_designs}")
            for _ in range(times_per_design):
                hour, minute, second = all_times[time_index % len(all_times)]
                time_index += 1
                filename = draw_digital(hour, minute, second, sample_id, design)
                writer.writerow({
                    "sample_id": sample_id,
                    "design_id": design["design_id"],
                    "filename": filename,
                    "hour": hour,
                    "minute": minute,
                    "second": second,
                    "time_string": f"{hour:02d}:{minute:02d}:{second:02d}"
                })
                sample_id += 1

    total = num_designs * times_per_design
    print(f"Generated {total} images and saved metadata to {CSV_FILE}")


if __name__ == "__main__":
    generate_dataset(num_designs=6, times_per_design=250)
