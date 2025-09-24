import socket
import ssl
from django.core.management.base import BaseCommand
from django.conf import settings


class Command(BaseCommand):
    help = "Diagnose SMTP configuration: resolve host, connect, start TLS, and report settings."

    def add_arguments(self, parser):
        parser.add_argument('--timeout', type=float, default=10.0)

    def handle(self, *args, **opts):
        backend = getattr(settings, 'EMAIL_BACKEND', '')
        self.stdout.write(f"EMAIL_BACKEND: {backend}")
        if not backend.endswith('smtp.EmailBackend'):
            self.stdout.write(self.style.WARNING("Not using SMTP backend; set EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend in .env to test sending."))
            return

        host = getattr(settings, 'EMAIL_HOST', '')
        port = int(getattr(settings, 'EMAIL_PORT', 587))
        use_tls = bool(getattr(settings, 'EMAIL_USE_TLS', True))
        user = getattr(settings, 'EMAIL_HOST_USER', '')
        from_addr = getattr(settings, 'DEFAULT_FROM_EMAIL', '')

        self.stdout.write(f"EMAIL_HOST: {host}")
        self.stdout.write(f"EMAIL_PORT: {port}")
        self.stdout.write(f"EMAIL_USE_TLS: {use_tls}")
        self.stdout.write(f"EMAIL_HOST_USER: {user}")
        self.stdout.write(f"DEFAULT_FROM_EMAIL: {from_addr}")

        if not host:
            self.stderr.write(self.style.ERROR("EMAIL_HOST is empty"))
            return

        # DNS resolution
        try:
            addrs = socket.getaddrinfo(host, port, proto=socket.IPPROTO_TCP)
            ips = sorted({a[4][0] for a in addrs})
            self.stdout.write(f"Resolved {host} -> {', '.join(ips)}")
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"DNS resolution failed: {e}"))
            return

        # TCP connect
        timeout = float(opts['timeout'])
        try:
            sock = socket.create_connection((host, port), timeout=timeout)
            self.stdout.write(self.style.SUCCESS(f"TCP connect OK: {host}:{port}"))
        except Exception as e:
            self.stderr.write(self.style.ERROR(f"TCP connect failed: {e}"))
            return

        # Read banner (optional)
        try:
            sock.settimeout(5)
            banner = sock.recv(256).decode(errors='ignore')
            if banner:
                self.stdout.write(f"Banner: {banner.strip()}")
        except Exception:
            pass

        # STARTTLS if configured
        if use_tls:
            try:
                # Minimal STARTTLS negotiation: send EHLO and STARTTLS, then wrap
                sock.sendall(b"EHLO localhost\r\n")
                _ = sock.recv(2048)
                sock.sendall(b"STARTTLS\r\n")
                _ = sock.recv(2048)
                context = ssl.create_default_context()
                tls_sock = context.wrap_socket(sock, server_hostname=host)
                tls_sock.sendall(b"EHLO localhost\r\n")
                resp = tls_sock.recv(2048).decode(errors='ignore')
                self.stdout.write(self.style.SUCCESS("STARTTLS OK"))
                self.stdout.write("TLS EHLO response (truncated):\n" + resp.split('\n')[0])
                tls_sock.close()
            except Exception as e:
                self.stderr.write(self.style.ERROR(f"STARTTLS failed: {e}"))
                try:
                    sock.close()
                except Exception:
                    pass
                return
        else:
            self.stdout.write("TLS not requested; skipping STARTTLS test.")

        self.stdout.write(self.style.SUCCESS("SMTP diagnostics completed."))
