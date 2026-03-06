This is a python script to add a bunch of objects in a Path of Exile hideout in a formation. Currently it only supports Oriathan Child, but that is subject to change.

"""
--help:
usage: hideout-generator.py [--help] [-p POINTS] [-h HEIGHT] [-w WIDTH] [-s SPACING] [-a] [-r ROTATION] [-l LAYERS] [--layer-step LAYER_STEP] [--layer-rotation LAYER_ROTATION]
                            [--shape {star,circle,spiral}] [--arms ARMS]

Generate a shape of objects for a Path of Exile hideout.

options:
  --help                Show this help message and exit
  -p, --points POINTS   Number of points on the star (default: 5)
  -h, --height HEIGHT   Height of shape, number between 0 and 390 (default: 190)
  -w, --width WIDTH     Width of shape, number between 0 and 390 (default: 190)
  -s, --spacing SPACING
                        Place an item every N tiles along the outline (default: 4)
  -a, --ascii           Render out ascii of the shape(default=False)
  -r, --rotation ROTATION
                        Change the rotation of the shape
  -l, --layers LAYERS   Number of concentric stars to generate (default: 1)
  --layer-step LAYER_STEP
                        Radius increase per layer in tiles (default: 10)
  --layer-rotation LAYER_ROTATION
                        Additional rotation in degrees (0-360) applied to each successive layer (default: 0.0)
  --shape {star,circle,spiral}
                        Shape to generate (default: star)
  --arms ARMS           Number of spiral arms (spiral only, default: 1)
"""