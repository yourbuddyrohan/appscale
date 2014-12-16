""" Top level server for the Search API. """
from search_api import SearchService

import tornado.httpserver
import tornado.httputil
import tornado.ioloop
import tornado.web
import time
# Default port for the search API web server.
DEFAULT_PORT = 53423

class MainHandler(tornado.web.RequestHandler):
  """ Main handler class. """
  
  def initialize(self, search):
    """ Class for initializing search service web handler. """
    self.search_service = search

  @tornado.web.asynchronous
  def post(self):
    request = self.request
    http_request_data = request.body
    app_data = request.headers['appdata']
    pb_type = request.headers['protocolbuffertype']
    app_data  = app_data.split(':')
    app_id = app_data[0]
    if pb_type == "Request":
      response = self.search_service.remote_request(app_id, app_data)
    else:
      response = self.search_service.unknown_request(pb_type)

    request.connection.write_headers(
      tornado.httputil.ResponseStartLine('HTTP/1.1', 200, 'OK'),
      tornado.httputil.HTTPHeaders({"Content-Length": str(len(response))}))
    request.connection.write(response)
    request.connection.finish()

  

def get_application():
  """ Retrieves the application to feed into tornado. """
  return tornado.web.Application([
    (r"/?", MainHandler, dict(search_service=SearchService())),
    ], )

if __name__ == "__main__":
  logging.info("Starting server on port {0}".format(DEFAULT_PORT))
  http_server = tornado.httpserver.HTTPServer(get_application())
  http_server.bind(DEFAULT_PORT)
  http_server.start(0)
  tornado.ioloop.IOLoop.instance().start()
