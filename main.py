#!/usr/bin/env python3
"""
BBS Server Application Entry Point

This is the main entry point for the BBS (Bulletin Board System) server.
Always use this file to start the application, never run bbs_server.py directly.

Usage:
    uv run python main.py [options]

Examples:
    uv run python main.py                    # Start with default settings
    uv run python main.py --port 2324       # Start on custom port
    uv run python main.py --db-path ./custom.db  # Use custom database
"""
import argparse
import os
import sys
from pathlib import Path

# Import the BBS server module
import bbs_server


def parse_arguments():
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='BBS Server - Telnet-style Bulletin Board System',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s                              Start BBS on default port 2323
  %(prog)s --port 2324                  Start BBS on port 2324
  %(prog)s --db-path ./custom.db        Use custom database file
  %(prog)s --port 2324 --db-path ./test.db  Custom port and database

For more information, see README.md or AGENT.md
        """
    )
    
    parser.add_argument(
        '--port',
        type=int,
        default=2323,
        help='Port to listen on (default: 2323)'
    )
    
    parser.add_argument(
        '--db-path',
        type=str,
        default='./data/bbs.sqlite3',
        help='Path to SQLite database file (default: ./data/bbs.sqlite3)'
    )
    
    parser.add_argument(
        '--host',
        type=str,
        default='0.0.0.0',
        help='Host to bind to (default: 0.0.0.0)'
    )
    
    parser.add_argument(
        '--init-only',
        action='store_true',
        help='Initialize database and exit (useful for setup)'
    )
    
    parser.add_argument(
        '--version',
        action='version',
        version='BBS Server 1.0.0'
    )
    
    return parser.parse_args()


def setup_environment(args):
    """Set up environment variables based on command line arguments."""
    # Set environment variables that bbs_server.py reads
    os.environ['BBS_PORT'] = str(args.port)
    os.environ['BBS_DB_PATH'] = args.db_path
    
    # Ensure database directory exists
    db_path = Path(args.db_path)
    db_path.parent.mkdir(parents=True, exist_ok=True)
    
    print(f"🚀 BBS Server Configuration:")
    print(f"   Host: {args.host}")
    print(f"   Port: {args.port}")
    print(f"   Database: {args.db_path}")
    print(f"   Database directory: {db_path.parent}")


def main():
    """Main application entry point."""
    try:
        # Parse command line arguments
        args = parse_arguments()
        
        # Setup environment
        setup_environment(args)
        
        # Initialize database
        print("📊 Initializing database...")
        bbs_server.init_db()
        print("✅ Database initialized successfully")
        
        if args.init_only:
            print("🏁 Database initialization complete. Exiting.")
            return
        
        # Import and run the main server function
        print("🌐 Starting BBS server...")
        print("   Use Ctrl+C to stop the server")
        print(f"   Connect via: telnet localhost {args.port}")
        print("-" * 50)
        
        # Run the server (this will block until shutdown)
        import asyncio
        asyncio.run(bbs_server.main())
        
    except KeyboardInterrupt:
        print("\n🛑 Server stopped by user")
    except Exception as e:
        print(f"❌ Error starting BBS server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
