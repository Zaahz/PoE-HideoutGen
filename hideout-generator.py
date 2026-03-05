import argparse, math, pprint as pp, json, os, sys


"""
with open(os.path.join(os.path.dirname(__file__), 'input.hideout'), 'r') as file:
#with open(os.path.dirname(os.path.abspath(sys.argv[0])) + "/input.hideout") as file:
    #hideout_data = json.load(file)
    hideout_data = json.loads(file.decode('utf-8-sig'))
    print(f"Hideout data loaded: {hideout_data}")
"""

hideout_data = json.load(open('input.hideout', encoding='utf-8-sig'))
#pp.pprint(hideout_data)

x_min_value = 160
y_min_value = 160
x_max_value = 550
y_max_value = 550

# There are a maximum number of 750 items allowed within a hideout,
# but ~30 items are already taken for chests, crafting bench, questgivers etc depening on league.
maximum_amount_of_items = 720


def star_vertices(
    cx: float,
    cy: float,
    outer_r: float,
    inner_r: float,
    points: int = 5,
    rotation: float = -math.pi / 2,
) -> list[tuple[float, float]]:
    """Return the 2*points float vertices of a star polygon."""
    verts = []
    # A star with N points has 2*N vertices: N outer tips and N inner notches.
    # We step around the circle in increments of pi/points (half the full slice),
    # alternating between the outer and inner radius at each step.
    for i in range(points * 2):
        angle = math.pi * i / points + rotation  # angle for this vertex
        r = outer_r if i % 2 == 0 else inner_r   # even = tip, odd = notch
        verts.append((cx + r * math.cos(angle), cy + r * math.sin(angle)))
    #pp.pprint(verts)
    return verts


def bresenham_line(
    x0: int, y0: int, x1: int, y1: int
) -> list[tuple[int, int]]:
    """Return all integer grid cells along the line from (x0,y0) to (x1,y1)."""
    cells = []
    dx = abs(x1 - x0)          # total horizontal distance
    dy = abs(y1 - y0)          # total vertical distance
    sx = 1 if x0 < x1 else -1  # step direction on x axis
    sy = 1 if y0 < y1 else -1  # step direction on y axis

    # err tracks the accumulated rounding error.
    # When it tips over the threshold we step in the minor axis direction.
    err = dx - dy
    x, y = x0, y0
    while True:
        cells.append((x, y))
        if x == x1 and y == y1:
            break
        e2 = 2 * err
        if e2 > -dy:   # error is large enough to step horizontally
            err -= dy
            x += sx
        if e2 < dx:    # error is large enough to step vertically
            err += dx
            y += sy
    return cells


def star_outline(
    cx: float,
    cy: float,
    outer_r: float,
    inner_r: float,
    points: int = 5,
    rotation: float = -math.pi / 2,
    spacing: int = 1,
) -> list[tuple[int, int]]:
    """Return deduplicated integer tile positions forming the star outline."""
    # Generate the continuous (float) vertices of the star polygon.
    verts = star_vertices(cx, cy, outer_r, inner_r, points, rotation)

    # Snap each float vertex to the nearest integer grid tile.
    int_verts = [(round(x), round(y)) for x, y in verts]

    seen: set[tuple[int, int]] = set()
    result: list[tuple[int, int]] = []
    n = len(int_verts)

    # step_counter tracks position across the entire outline so spacing is
    # applied globally rather than resetting at each edge.
    step_counter = 0

    # Walk every edge of the polygon and collect all grid tiles it passes through.
    # The modulo on the second index wraps the last vertex back to the first,
    # closing the star outline.
    for i in range(n):
        x0, y0 = int_verts[i]
        x1, y1 = int_verts[(i + 1) % n]
        for cell in bresenham_line(x0, y0, x1, y1):
            if cell not in seen:
                seen.add(cell)
                # Only keep this tile if it falls on the spacing interval.
                if step_counter % spacing == 0:
                    result.append(cell)
                step_counter += 1
    return result


def circle_outline(
    cx: float,
    cy: float,
    r: float,
    spacing: int = 1,
) -> list[tuple[int, int]]:
    """Return deduplicated integer tile positions forming a circle outline."""
    # Sample enough vertices around the circumference so adjacent chords
    # stay close to the true curve (one vertex per unit of arc length).
    n_verts = max(8, round(2 * math.pi * r))
    int_verts = [
        (round(cx + r * math.cos(2 * math.pi * i / n_verts)),
         round(cy + r * math.sin(2 * math.pi * i / n_verts)))
        for i in range(n_verts)
    ]

    seen: set[tuple[int, int]] = set()
    result: list[tuple[int, int]] = []
    step_counter = 0

    for i in range(n_verts):
        x0, y0 = int_verts[i]
        x1, y1 = int_verts[(i + 1) % n_verts]
        for cell in bresenham_line(x0, y0, x1, y1):
            if cell not in seen:
                seen.add(cell)
                if step_counter % spacing == 0:
                    result.append(cell)
                step_counter += 1
    return result


def spiral_outline(
    cx: float,
    cy: float,
    start_r: float,
    rotations: int,
    growth_per_rotation: float,
    rotation: float = 0.0,
    spacing: int = 1,
) -> list[tuple[int, int]]:
    """Return deduplicated integer tile positions forming an Archimedean spiral.

    The spiral starts at start_r and grows by growth_per_rotation each full
    revolution. rotations controls how many times it winds around the center.
    """
    end_r = start_r + rotations * growth_per_rotation
    total_angle = rotations * 2 * math.pi
    # Sample one point per unit of arc length so the path stays smooth.
    avg_r = (start_r + end_r) / 2
    n_points = max(16, round(total_angle * avg_r))

    # Build sample points along the spiral (open path — no wrap-around).
    int_verts = []
    for i in range(n_points + 1):
        t = i / n_points
        angle = rotation + t * total_angle
        r = start_r + t * rotations * growth_per_rotation
        int_verts.append((round(cx + r * math.cos(angle)), round(cy + r * math.sin(angle))))

    seen: set[tuple[int, int]] = set()
    result: list[tuple[int, int]] = []
    step_counter = 0

    for i in range(len(int_verts) - 1):
        x0, y0 = int_verts[i]
        x1, y1 = int_verts[i + 1]
        for cell in bresenham_line(x0, y0, x1, y1):
            if cell not in seen:
                seen.add(cell)
                if step_counter % spacing == 0:
                    result.append(cell)
                step_counter += 1
    return result


def render_ascii(tiles: list[tuple[int, int]]) -> None:
    """Print an ASCII grid showing the tile positions."""
    if not tiles:
        print("(no tiles)")
        return

    # Find the bounding box of all occupied tiles.
    xs = [x for x, _ in tiles]
    ys = [y for _, y in tiles]
    min_x, max_x = min(xs), max(xs)
    min_y, max_y = min(ys), max(ys)

    tile_set = set(tiles)  # set for O(1) membership checks

    # Print row by row from top to bottom; '#' marks an occupied tile.
    for y in range(min_y, max_y + 1):
        row = ""
        for x in range(min_x, max_x + 1):
            row += "#" if (x, y) in tile_set else "."
        print(row)


def write_hideout(hideout_data, new_entries, output_path):
    """Write a hideout file, supporting duplicate doodad keys for multiple instances."""
    # The .hideout format allows duplicate keys (e.g. many "Oriathan Child" entries),
    # which json.dump cannot produce. We build the doodads section manually as a
    # sequence of raw JSON blocks.
    doodad_lines = []
    all_doodads = list(hideout_data.get("doodads", {}).items()) + new_entries
    for i, (name, data) in enumerate(all_doodads):
        comma = "," if i < len(all_doodads) - 1 else ""
        block = (
            f'    {json.dumps(name)}: {{\n'
            f'      "hash": {data["hash"]},\n'
            f'      "x": {data["x"]},\n'
            f'      "y": {data["y"]},\n'
            f'      "r": {data["r"]},\n'
            f'      "fv": {data["fv"]}\n'
            f'    }}{comma}'
        )
        doodad_lines.append(block)

    output = (
        f'{{\n'
        f'  "version": {json.dumps(hideout_data["version"])},\n'
        f'  "language": {json.dumps(hideout_data["language"])},\n'
        f'  "hideout_name": {json.dumps(hideout_data["hideout_name"])},\n'
        f'  "hideout_hash": {json.dumps(hideout_data["hideout_hash"])},\n'
        f'  "doodads": {{\n'
        + "\n".join(doodad_lines) + "\n"
        f'  }}\n'
        f'}}'
    )

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output)


def add_to_hideout_file(tiles, hideout_data, cx, cy):
    new_entries = []
    for x, y in tiles:
        # Angle in radians from this tile pointing toward the center.
        angle = math.atan2(cy - y, cx - x)
        # Convert to a 16-bit unsigned integer (0 = 0°, 65536 = 360°).
        r = (round(angle % (2 * math.pi) / (2 * math.pi) * 65536) % 65536) + 16384
        new_entries.append(
            ("Oriathan Child", {"hash": 2808502392, "x": x, "y": y, "r": r, "fv": 0})
        )
    write_hideout(hideout_data, new_entries, "output.hideout")
    print(f"Written to output.hideout ({len(new_entries)} Oriathan Children added)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Generate a shape of objects for a Path of Exile hideout.", add_help=False)
    parser.add_argument("--help", action="help", help="Show this help message and exit")
    parser.add_argument("-p", "--points", type=int, default=5, help="Number of points on the star (default: 5)")
    parser.add_argument("-h", "--height", type=int, default=190, help="Height of shape, number between 0 and 390 (default: 190)")
    parser.add_argument("-w", "--width", type=int, default=190, help="Width of shape, number between 0 and 390 (default: 190)")
    parser.add_argument("-s", "--spacing", type=int, default=4, help="Place an item every N tiles along the outline (default: 4)")
    parser.add_argument("-a", "--ascii", action='store_true', help="Render out ascii of the shape(default=False)")
    parser.add_argument("-r", "--rotation", type=float, default=-math.pi / 2, help="Change the rotation of the shape")
    parser.add_argument("-l", "--layers", type=int, default=1, help="Number of concentric stars to generate (default: 1)")
    parser.add_argument("--layer-step", type=int, default=10, help="Radius increase per layer in tiles (default: 10)")
    parser.add_argument("--layer-rotation", type=float, default=0.0, help="Additional rotation in degrees (0-360) applied to each successive layer (default: 0.0)")
    parser.add_argument("--shape", choices=["star", "circle", "spiral"], default="star", help="Shape to generate (default: star)")
    parser.add_argument("--arms", type=int, default=1, help="Number of spiral arms (spiral only, default: 1)")
    args = parser.parse_args()

    # Place the star at the center of the valid hideout area.
    cx = (x_min_value + x_max_value) / 2  # 355
    cy = (y_min_value + y_max_value) / 2  # 355

    # outer_r is half the smaller of width/height so the star fits within both.
    outer_r = min(args.width, args.height) / 2
    # inner_r keeps the same notch-to-tip ratio as the original defaults (3.5/8).
    inner_r = outer_r * (3.5 / 8)

    # Move the Waypoint to the center of the star.
    hideout_data["doodads"]["Waypoint"]["x"] = round(cx)
    hideout_data["doodads"]["Waypoint"]["y"] = round(cy)

    seen: set[tuple[int, int]] = set()
    tiles: list[tuple[int, int]] = []

    if args.shape == "spiral":
        # For a spiral, --layers = number of rotations, --layer-step = inner
        # (starting) radius. The spiral grows from layer_step outward to outer_r,
        # dividing the radial range evenly across the rotations so the turns are
        # spread out and clearly visible rather than bunched at a large radius.
        inner_r_spiral = args.layer_step
        growth_per_rotation = (outer_r - inner_r_spiral) / max(args.layers, 1)

        # Generate a circle at the inner radius so all arms share a visible centre.
        for tile in circle_outline(cx=cx, cy=cy, r=inner_r_spiral, spacing=args.spacing):
            if tile not in seen:
                seen.add(tile)
                tiles.append(tile)

        # Each arm is offset by an equal fraction of a full turn so they spread
        # evenly around the centre (e.g. 2 arms → 0° and 180° apart).
        for arm in range(args.arms):
            arm_rotation = args.rotation + arm * (2 * math.pi / args.arms)
            for tile in spiral_outline(
                cx=cx, cy=cy, start_r=inner_r_spiral, rotations=args.layers,
                growth_per_rotation=growth_per_rotation, rotation=arm_rotation,
                spacing=args.spacing,
            ):
                if tile not in seen:
                    seen.add(tile)
                    tiles.append(tile)
    else:
        # Generate one ring per layer, each growing by layer_step in radius.
        # A set tracks seen tiles so overlapping layers don't produce duplicates.
        for i in range(args.layers):
            layer_outer_r = outer_r + i * args.layer_step
            layer_inner_r = layer_outer_r * (3.5 / 8)
            layer_rotation = args.rotation - i * math.radians(args.layer_rotation)
            if args.shape == "circle":
                layer_tiles = circle_outline(cx=cx, cy=cy, r=layer_outer_r, spacing=args.spacing)
            else:
                layer_tiles = star_outline(cx=cx, cy=cy, outer_r=layer_outer_r, inner_r=layer_inner_r, points=args.points, spacing=args.spacing, rotation=layer_rotation)
            for tile in layer_tiles:
                if tile not in seen:
                    seen.add(tile)
                    tiles.append(tile)

    if len(tiles) > maximum_amount_of_items:
        print(f"Error: shape requires {len(tiles)} tiles, which exceeds the maximum of {maximum_amount_of_items}.")
        print("Try reducing --width, --height, --points, or increasing --spacing.")
        exit(1)
    #pp.pprint(tiles)
    print(f"Tile count: {len(tiles)}")
    #print(args.ascii)
    if args.ascii == True:
        render_ascii(tiles)
    add_to_hideout_file(tiles, hideout_data, cx, cy)

