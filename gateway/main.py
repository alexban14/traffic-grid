import uvicorn
from server import ThreadingTCPServer, SocksProxy

if __name__ == "__main__":
    server = ThreadingTCPServer(("0.0.0.0", 1080), SocksProxy)
    print("SOCKS5 Proxy Server started on port 1080")
    server.serve_forever()