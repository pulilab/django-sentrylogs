import os
from optparse import make_option
from django.core.management.base import NoArgsCommand, CommandError

class Command(NoArgsCommand):
    help = 'Calls SentryLogs'
    can_import_settings = True
    option_list = NoArgsCommand.option_list + (
        make_option('--foreground',
            action='store_true',
            dest='foreground',
            default=False,
            help='Run in the foreground'),
        make_option('--nginxerrorpath',
            dest='nginxerrorpath',
            default=False,
            help='Nginx error log path'),
        )

    def handle(self, **options):
        from django.conf import settings as djsettings
        os.environ['SENTRY_DSN'] = djsettings.RAVEN_CONFIG['dsn']
        if options['nginxerrorpath']:
            os.environ['NGINX_ERROR_PATH'] = options['nginxerrorpath']
        elif getattr(djsettings, 'NGINX_ERROR_PATH', False):
            os.environ['NGINX_ERROR_PATH'] = djsettings.NGINX_ERROR_PATH

        if not options['foreground']:
            from sentrylogs.conf import settings
            from sentrylogs.daemonize import createDaemon

            retCode = createDaemon()

            procParams = """
return code = %s
process ID = %s
parent process ID = %s
process group ID = %s
session ID = %s
user ID = %s
effective user ID = %s
real group ID = %s
effective group ID = %s
           """ % (retCode, os.getpid(), os.getppid(), os.getpgrp(), os.getsid(0),
            os.getuid(), os.geteuid(), os.getgid(), os.getegid())

            self.stdout.write(procParams)

        from sentrylogs import nginx
