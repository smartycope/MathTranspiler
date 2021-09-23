import urllib, urllib3

def latex2svg(latexcode):
    """
    Turn LaTeX string to an SVG formatted string using the online SVGKit
    found at: http://svgkit.sourceforge.net/tests/latex_tests.html
    """
    txdata = urllib.parse.urlencode({"latex": latexcode})
    url = "http://svgkit.sourceforge.net/cgi-bin/latex2svg.py"
    req = urllib.request.Request(url, txdata)
    return urllib.request.urlopen(req).read()
