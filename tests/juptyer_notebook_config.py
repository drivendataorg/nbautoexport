# >>> nbautoexport initialize >>>
try:
    from nbautoexport import post_save

    if callable(c.FileContentsManager.post_save_hook):
        old_post_save = c.FileContentsManager.post_save_hook

        def _post_save(model, os_path, contents_manager):
            old_post_save(model, os_path, contents_manager)
            post_save(model, os_path, contents_manager)

        c.FileContentsManager.post_save_hook = _post_save
    else:
        c.FileContentsManager.post_save_hook = post_save
except:
    pass
# <<< nbautoexport initialize <<<
