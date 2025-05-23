import os
import json
import tempfile
import pytest
from pathlib import Path
from SimpleOSMRenderer.renderer import (  
    summarize_frames,
    color_hex_to_folium_icon,
    create_map_for_frame,
    main
)

def test_summarize_frames_generates_html():
    """Test HTML generation with special characters and frame indexing."""
    frames = [
        {"description": "Tag at location A"},
        {"description": "Emergency at <location B>"},
        {"description": ""}  # Test empty description
    ]
    html_output = summarize_frames(frames)

    assert "<!DOCTYPE html>" in html_output
    assert "frame2" in html_output  # Verify indexing
    assert 'class="frameLine"' in html_output
    assert "Emergency at &lt;location B&gt;" in html_output

@pytest.mark.parametrize("hex_code,expected_color", [
    ("#FF0000", "red"),        # Exact match
    ("00FF00", "green"),       # Missing #
    ("FF0", "yellow"),         # Shortened (approximate)
    ("#808080", "gray"),       # Neutral color
    ("invalid", "blue"),       # Fallback
    (None, "blue"),            # None input
])
def test_color_hex_to_folium_icon(hex_code, expected_color):
    """Test color conversion with various input formats."""
    color = color_hex_to_folium_icon(hex_code)
    assert color == expected_color

def test_create_map_for_frame_outputs_valid_html():
    """Verify generated map contains expected elements."""
    test_frame = {
        "tags": [{
            "position": [51.5, -0.1],
            "icon": "hospital",
            "color": "#FF0000",
            "description": "Test Hospital"
        }],
        "lines": [{
            "start": [51.5, -0.1],
            "end": [51.6, -0.1],
            "color": "#0000FF"
        }]
    }

    with tempfile.TemporaryDirectory() as tmpdir:
        output_path = Path(tmpdir) / "map.html"
        create_map_for_frame(test_frame, None, str(output_path))
        
        assert output_path.exists()
        content = output_path.read_text(encoding='utf-8')
        
        # Verify critical components
        assert "leaflet.js" in content  # Folium dependency
        assert "Test Hospital" in content
        assert "[51.5, -0.1]" in content  # Coordinate in JS
        assert "<!DOCTYPE html>" in content

def test_main_function(tmp_path):
    """Integration test for the main render pipeline."""
    # Create test JSON
    test_data = {
        "frames": [{
            "description": "Test Frame",
            "tags": [{
                "position": [51.5, -0.1],
                "description": "Test Point"
            }]
        }]
    }
    
    input_file = tmp_path / "test.json"
    output_dir = tmp_path / "output"
    
    with open(input_file, 'w') as f:
        json.dump(test_data, f)
    
    # Run main function
    main(input_file=str(input_file), output_dir=str(output_dir))
    
    # Verify outputs
    assert (output_dir / "all_frames.html").exists()
    assert (output_dir / "event_0.html").exists()
    assert (output_dir / "_master.html").exists()