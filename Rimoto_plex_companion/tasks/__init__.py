from Rimoto_plex_companion.tasks.scanner import Scanner


scanner_task = Scanner()
scanner_data = {
    'id': scanner_task.thread.ident,
    'is_alive' : scanner_task.thread.is_alive()
}
