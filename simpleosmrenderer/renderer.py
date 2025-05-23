"""
Simple OSM Renderer using Folium

A Python package for rendering OpenStreetMap data and custom routes using Folium maps.
"""

import json
import os
import folium
from pathlib import Path
from typing import List, Dict, Optional, Tuple

# Constants
GOOGLE_MAPS_API_KEY = os.getenv('GOOGLE_MAPS_API_KEY', '')
DEFAULT_INPUT_FILE = "route.json"
DEFAULT_OUTPUT_DIR = "route_output"

def summarize_frames(frames: List[Dict]) -> str:
    """
    Generate an HTML summary of all frames/events.
    
    Args:
        frames: List of frame dictionaries from JSON input
        
    Returns:
        HTML string with all frames listed
    """
    html = []
    html.append("<!DOCTYPE html>")
    html.append("<html>")
    html.append("<head>")
    html.append("<meta charset='utf-8' />")
    html.append("<title>All Frames</title>")
    html.append("<style>")
    html.append("""
      body { margin:0; padding:0; font-family: sans-serif; }
      h3 { background: #eee; margin: 0; padding: 8px; }
      .frameLine {
        display: block;
        padding: 5px;
        border-bottom: 1px solid #ccc;
        text-decoration: none;
        color: #000;
      }
      .frameLine:target {
        background-color: yellow;
      }
    """)
    html.append("</style>")
    html.append("</head>")
    html.append("<body>")
    html.append("<h3>All Frames (Events)</h3>")
    html.append("<div>")
    for i, frame in enumerate(frames):
        anchor_id = f"frame{i}"
        desc_safe = frame["description"].replace("<", "&lt;").replace(">", "&gt;")
        line_html = (
            f"<a id='{anchor_id}' name='{anchor_id}' "
            f"class='frameLine'>Frame {i}: {desc_safe}</a>"
        )
        html.append(line_html)
    html.append("</div>")
    html.append("</body>")
    html.append("</html>")
    return "\n".join(html)

def color_hex_to_folium_icon(hex_color: str) -> str:
    """
    Convert hex color code to nearest named Folium icon color.
    
    Args:
        hex_color: Color in hex format (e.g., '#FF0000' or 'FF0000')
        
    Returns:
        Closest named Folium color (e.g., 'red')
    """
    c = hex_color.strip().lower()
    if c.startswith("#"):
        c = c[1:]
    if len(c) == 3:
        c = "".join(ch*2 for ch in c)
    
    try:
        r = int(c[0:2], 16)
        g = int(c[2:4], 16)
        b = int(c[4:6], 16)
    except ValueError:
        return "blue"
    
    named_colors = {
        "red": (255, 0, 0), "blue": (0, 0, 255), "green": (0, 255, 0),
        "purple": (128, 0, 128), "orange": (255, 165, 0), "darkred": (139, 0, 0),
        "lightred": (255, 102, 102), "beige": (245, 245, 220),
        "darkblue": (0, 0, 139), "darkgreen": (0, 100, 0),
        "cadetblue": (95, 158, 160), "darkpurple": (48, 25, 52),
        "white": (255, 255, 255), "pink": (255, 192, 203),
        "lightblue": (173, 216, 230), "lightgreen": (144, 238, 144),
        "gray": (128, 128, 128), "black": (0, 0, 0), "lightgray": (211, 211, 211),
    }
    
    best_color = "blue"
    best_dist = float("inf")
    for name, (nr, ng, nb) in named_colors.items():
        dist_sq = (r - nr)**2 + (g - ng)**2 + (b - nb)**2
        if dist_sq < best_dist:
            best_dist = dist_sq
            best_color = name
    return best_color

def create_map_for_frame(frame: Dict, global_bounds: Optional[List[List[float]]], output_path: str) -> None:
    """
    Generate a Folium map for a single frame.
    
    Args:
        frame: Dictionary containing frame data
        global_bounds: Fallback map bounds [[min_lat, min_lng], [max_lat, max_lng]]
        output_path: Path to save the HTML file
    """
    all_coords = []
    for tag in frame.get("tags", []):
        all_coords.append(tag["position"])
    for line in frame.get("lines", []):
        all_coords.append(line["start"])
        all_coords.append(line["end"])
    
    # Initialize map with appropriate tiles
    if GOOGLE_MAPS_API_KEY: 
        tile_url = f"https://mt1.google.com/vt/lyrs=m&x={{x}}&y={{y}}&z={{z}}&key={GOOGLE_MAPS_API_KEY}"
        m = folium.Map(tiles=None)
        folium.TileLayer(
            tiles=tile_url,
            attr="Google Maps",
            name="Google Maps",
            control=True
        ).add_to(m)
    else:
        m = folium.Map()
    
    # Set map bounds
    if all_coords:
        lats, lngs = zip(*all_coords)
        frame_bounds = [[min(lats), min(lngs)], [max(lats), max(lngs)]]
        m.fit_bounds(frame_bounds)
    elif global_bounds:
        m.fit_bounds(global_bounds)
    
    # Add markers
    for tag in frame.get("tags", []):
        lat, lng = tag["position"]
        icon_type = tag.get("icon", "info-sign")
        color_hex = tag.get("color", "#0000FF")
        desc_text = tag.get("description", "")
        folium_color = color_hex_to_folium_icon(color_hex)
        popup_str = f"{desc_text} (icon: {icon_type})"
        folium.Marker(
            location=[lat, lng],
            popup=popup_str,
            icon=folium.Icon(color=folium_color, icon=icon_type, prefix="fa")
        ).add_to(m)
    
    # Add lines
    for line in frame.get("lines", []):
        folium.PolyLine(
            locations=[line["start"], line["end"]],
            color=line["color"],
            weight=4
        ).add_to(m)

    m.save(output_path)

def generate_master_html(output_dir: str, total_frames: int) -> None:
    """
    Create the master HTML file that controls all frames.
    
    Args:
        output_dir: Directory to save the file
        total_frames: Number of frames available
    """
    master_html_path = os.path.join(output_dir, "_master.html")
    with open(master_html_path, "w", encoding="utf-8") as f:
        f.write(f"""<!DOCTYPE html>
<html>
<head>
  <meta charset="utf-8" />
  <title>Frames Master View</title>
  <style>
    body {{
      margin: 0;
      padding: 0;
      display: flex;
      flex-direction: column;
      height: 100vh;
    }}
    #controls {{
      background: #ececec;
      padding: 5px;
      flex: 0 0 auto;
    }}
    #mainContainer {{
      flex: 1 1 auto;
      display: flex;
      flex-direction: row;
      height: calc(100vh - 40px);
    }}
    #leftPane, #rightPane {{
      flex: 1 1 50%;
      border: none;
    }}
    button {{
      margin: 0 10px;
      padding: 6px 12px;
      cursor: pointer;
    }}
  </style>
</head>
<body>
  <div id="controls">
    <button id="prevBtn">Previous</button>
    <span id="info"></span>
    <button id="nextBtn">Next</button>
  </div>

  <div id="mainContainer">
    <iframe id="leftPane"></iframe>
    <iframe id="rightPane"></iframe>
  </div>

  <script>
    let current = 0;
    let maxIndex = {total_frames} - 1;
    const leftFrame = document.getElementById('leftPane');
    const rightFrame = document.getElementById('rightPane');
    const infoSpan = document.getElementById('info');

    function updateView() {{
      leftFrame.src = "event_" + current + ".html";
      rightFrame.src = "all_frames.html#frame" + current;
      infoSpan.textContent = "Frame " + current + " / " + maxIndex;
    }}

    document.getElementById('prevBtn').addEventListener('click', () => {{
      if (current > 0) {{
        current--;
        updateView();
      }}
    }});

    document.getElementById('nextBtn').addEventListener('click', () => {{
      if (current < maxIndex) {{
        current++;
        updateView();
      }}
    }});

    updateView();
  </script>
</body>
</html>
""")

def main(input_file: str = DEFAULT_INPUT_FILE, output_dir: str = DEFAULT_OUTPUT_DIR) -> None:
    """
    Main function to render OSM data from JSON to interactive maps.
    
    Args:
        input_file: Path to JSON input file (default: 'route.json')
        output_dir: Output directory for HTML files (default: 'route_output')
    """
    with open(input_file, "r", encoding="utf-8") as f:
        data = json.load(f)

    frames = data["frames"]
    os.makedirs(output_dir, exist_ok=True)

    # Calculate global bounds as fallback
    all_coords = []
    for frame in frames:
        for tag in frame.get("tags", []):
            all_coords.append(tag["position"])
        for line in frame.get("lines", []):
            all_coords.append(line["start"])
            all_coords.append(line["end"])
    
    if all_coords:
        lats, lngs = zip(*all_coords)
        global_bounds = [[min(lats), min(lngs)], [max(lats), max(lngs)]]
    else:
        global_bounds = None

    # Generate summary HTML
    all_frames_html = summarize_frames(frames)
    with open(os.path.join(output_dir, "all_frames.html"), "w", encoding="utf-8") as f:
        f.write(all_frames_html)

    # Generate individual maps
    for i, frame in enumerate(frames):
        create_map_for_frame(
            frame=frame,
            global_bounds=global_bounds,
            output_path=os.path.join(output_dir, f"event_{i}.html")
        )

    # Generate master controller
    generate_master_html(output_dir, len(frames))

    print(f"Rendering complete! Open '{os.path.join(output_dir, '_master.html')}' in your browser.")
    print("Use the Previous/Next buttons to navigate between frames.")

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(description="OSM Renderer using Folium")
    parser.add_argument("--input", default=DEFAULT_INPUT_FILE, help="Input JSON file")
    parser.add_argument("--output", default=DEFAULT_OUTPUT_DIR, help="Output directory")
    args = parser.parse_args()
    
    main(input_file=args.input, output_dir=args.output)