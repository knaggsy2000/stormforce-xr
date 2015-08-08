# StormForce XR

StormForce XR is a free open source program written in Python which connects to a Boltek LD-250 and/or Boltek EFM-100 lightning detector and displays lightning strikes in real-time on your desktop delivered via XMLRPC. Developed and tested with FreeBSD but should work with Linux and other POSIX environments as well as MS Windows.

Re-written using the v0.6.0 codebase of StormForce, StormForce XR has been split into two components - the server side and the client side. External packages have been reduced to just FIVE (with only one being optional) - serial (server only), pygame (client only), psycopg2 (server only), twisted (server only), and optionally matplotlib (client only) to simplify installation. The server side alone can provide a external (third-party) application access to the StormForce engine and dataset via XMLRPC, this means you can write your own client application which talks to the server should wish to do so. Everything is written to a PostgreSQL database so you can always talk to that directly should you feel the need to.

Please report any bugs using the issues section.

NOTICE: StormForce XR usually gets work done on it during the spring/summer months in the UK (around April-September) - this allows me to test the code with real storms and I can compare my data with other stations. So during autumn/winter the project will be very quiet. 



Status: Beta

Supported OS: FreeBSD, Linux, and Microsoft Windows

Supported Hardware: Boltek LD-250, and Boltek EFM-100

Need Testers for: Mac OS, Solaris, BeOS, and more!
