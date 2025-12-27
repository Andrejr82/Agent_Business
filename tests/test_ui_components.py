
import pytest
import plotly.express as px
from ui.ui_components import get_image_download_link

def test_get_image_download_link_class():
    """Test if the generated download link contains the class 'download-button'"""
    fig = px.bar(x=[1, 2, 3], y=[1, 3, 2])
    link = get_image_download_link(fig, "test_file", "Download Me")

    assert "class=\"download-button\"" in link
    assert "Download Me" in link
    assert "download=\"test_file" in link
