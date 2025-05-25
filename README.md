
# SimpleOSMRenderer

![Python Version](https://img.shields.io/badge/python-3.8%2B-blue)
[![License](https://img.shields.io/badge/license-MIT-green)](LICENSE)

A lightweight Python package for rendering OpenStreetMap data and custom routes as interactive Folium maps. Perfect for visualizing geographic routes, points of interest, and movement patterns.

---


## Features

- Convert JSON route data to interactive HTML maps
- Custom markers with icons/colors
- Polyline route visualization
- Master view with frame navigation
- Optional Google Maps tile integration


---

## Installation

### From GitHub
```bash
pip install git+https://github.com/gerritgr/SimpleOSMRenderer.git
```

---

### For Development
```bash
git clone https://github.com/gerritgr/SimpleOSMRenderer.git
cd SimpleOSMRenderer
pip install -e ".[test]"  # Install with test dependencies
```
---

## Quick Start

1. Prepare your route data as JSON ([example format](#input-format))
2. Render maps:
```python
from simpleosmrenderer.renderer import render_osm_maps

render_osm_maps(input_file="your_data.json", output_dir="maps")
```
3. Open `maps/_master.html` in your browser to navigate all frames!

## Input Format

Your JSON file should follow this structure:
```json
{
  "frames": [
    {
      "description": "Frame 1",
      "tags": [
        {
          "position": [lat, lng],
          "description": "Point A",
          "icon": "hospital",
          "color": "#FF0000"
        }
      ],
      "lines": [
        {
          "start": [lat1, lng1],
          "end": [lat2, lng2],
          "color": "#0000FF"
        }
      ]
    }
  ]
}
```


---

## Advanced Usage

### Google Maps Tiles
Set your API key as environment variable:
```python
import os
os.environ['GOOGLE_MAPS_API_KEY'] = 'your_key_here'
```

---

### Programmatic Access
```python
from simpleosmrenderer.renderer import create_map_for_frame

frame = {...}  # Your frame data
create_map_for_frame(frame, output_path="custom_map.html")
```
---

## Examples

See the `examples/` directory for:
- Sample input JSON files
- Generated output HTML files

---

## License

MIT - See [LICENSE](LICENSE) for details.

---
