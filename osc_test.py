from pythonosc import dispatcher
from pythonosc import osc_server

cur_port = 32323
cur_ip = "127.0.0.1"

cur_disp = dispatcher.Dispatcher()
cur_disp.map("/blue", print)
cur_disp.map("/red", print)

server = osc_server.ThreadingOSCUDPServer((cur_ip, cur_port), cur_disp)
print("Serving on {}".format(server.server_address))
server.serve_forever()
