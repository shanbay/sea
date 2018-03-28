import blinker


server_started = blinker.signal('server_started')
server_stopped = blinker.signal('server_stopped')
