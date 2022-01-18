import blinker


server_started = blinker.signal('server_started')
server_stopped = blinker.signal('server_stopped')
# send post_ready signal after app is ready
post_ready = blinker.signal('post_ready')
