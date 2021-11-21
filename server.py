from http.server import HTTPServer, BaseHTTPRequestHandler
import json
import random

def read_bytes(filename):
    with open(filename) as f:
        return encode(f.read())

def encode(data):
    return data.encode("utf-8")

def random_colour():
    return "#"+''.join([random.choice('0123456789ABCDEF') for j in range(6)])

def box():
    return '<div class="box" style="background: %s" hx-get="/click" hx-ext="event-header" hx-swap="outerHTML"></div>' % (random_colour())

def boxes(direction):
    return ('<div style="display:flex; flex-direction: %s">' % (direction)) + box() + box() + '</div>'

class RequestHandler (BaseHTTPRequestHandler):

    def handle_static(self):
        path = self.path
        if path == "/":
            path = "/index.html"
        if path.endswith(".js") or path.endswith(".html"):
            path = path[1:] # strip "/"
            self.wfile.write(read_bytes(path))
            return True

    def find_nearest_edge(self):
        event = json.loads(self.headers["Triggering-Event"])
        element = json.loads(self.headers["Triggering-Element"])
        x, y = event["offsetX"], event["offsetY"]
        width, height = element["offsetWidth"], element["offsetHeight"]
        distances = [("left", x), ("right", width - x), ("top", y), ("bottom", height - y)]
        nearestEdge, shortestDistance = min(distances, key = lambda x: x[1])
        return nearestEdge

    def handle_click(self):
        if self.path == "/click":
            nearestEdge = self.find_nearest_edge()
            direction = "row" if nearestEdge in ["left", "right"] else "column"
            self.wfile.write(encode(boxes(direction)))
            return True

    def handle_unknown(self):
        self.wfile.write(encode("<div>UNKNOWN PATH REQUESTED: %s</div>" % (self.path)))

    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.handle_static() or self.handle_click() or self.handle_unknown()

server = HTTPServer(server_address=('', 80), RequestHandlerClass=RequestHandler)
server.serve_forever()
