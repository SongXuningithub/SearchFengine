import argparse
import logging
from engine.api import app
from config.settings import FRONTEND_CONFIG

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)

def main():
    parser = argparse.ArgumentParser(description='Financial Search Engine API')
    parser.add_argument('--host', type=str, default=FRONTEND_CONFIG['host'],
                       help='Host to bind to')
    parser.add_argument('--port', type=int, default=FRONTEND_CONFIG['port'],
                       help='Port to bind to')
    parser.add_argument('--debug', action='store_true',
                       help='Enable debug mode')
    
    args = parser.parse_args()
    
    print(f"Starting Financial Search Engine API on {args.host}:{args.port}")
    print("Available endpoints:")
    print("  GET /api/search?q=<query> - Search documents")
    print("  GET /api/suggest?q=<query> - Get query suggestions")
    print("  GET /api/stats - Get search statistics")
    print("  GET /api/keywords - Get popular keywords")
    print("  GET /api/health - Health check")
    
    try:
        app.run(
            host=args.host,
            port=args.port,
            debug=args.debug or FRONTEND_CONFIG['debug']
        )
    except KeyboardInterrupt:
        print("\nSearch engine stopped by user")
    except Exception as e:
        logging.error(f"Search engine error: {e}")

if __name__ == "__main__":
    main() 