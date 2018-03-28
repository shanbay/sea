import blinker


before_rpc = blinker.signal('before_rpc')
after_rpc = blinker.signal('after_rpc')

server_started = blinker.signal('server_started')
server_stopped = blinker.signal('server_stopped')
