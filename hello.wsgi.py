def application(environ, start_response):
    status = '500'  # not okay till we get value from database
    status = '200 OK'
    output = 'Hello Richard.'

    response_headers = [('Content-type', 'text/plain'), ('Content-Length', str(len(output)))]
    start_response(status, response_headers)

    return [output]
