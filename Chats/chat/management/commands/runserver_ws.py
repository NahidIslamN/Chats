import os
import sys
import subprocess
import socket
import time
from django.core.management.base import BaseCommand
from django.core.management import call_command

def wait_for_port_available(port, max_wait=30):
    start_time = time.time()
    while time.time() - start_time < max_wait:
        try:
            with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
                s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
                s.bind(('0.0.0.0', port))
                return True
        except socket.error:
            print(f"Port {port} is still in use, waiting...")
            time.sleep(1)
    return False

class Command(BaseCommand):
    help = 'Runs the development server with WebSocket support'

    def add_arguments(self, parser):
        parser.add_argument(
            '--port',
            type=int,
            default=8000,
            help='Port to run the server on'
        )
        parser.add_argument(
            '--host',
            type=str,
            default='0.0.0.0',
            help='Host to run the server on'
        )

    def handle(self, *args, **options):
        port = options['port']
        host = options['host']

        # Wait for port to become available
        if not wait_for_port_available(port):
            self.stdout.write(
                self.style.ERROR(
                    f'Could not start server: Port {port} is still in use after waiting'
                )
            )
            return

        # Start Daphne server with WebSocket support
        self.stdout.write(self.style.SUCCESS('Starting server with WebSocket support...'))
        
        try:
            # Use Daphne for WebSocket support
            cmd = [
                sys.executable,
                '-m',
                'daphne',
                '--proxy-headers',
                '-b',
                host,
                '-p',
                str(port),
                'messenger.asgi:application'
            ]
            
            subprocess.run(cmd)
            
        except KeyboardInterrupt:
            self.stdout.write(self.style.SUCCESS('\nServer stopped by user'))
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Error starting server: {e}')
            ) 