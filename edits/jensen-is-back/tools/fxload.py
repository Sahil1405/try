import importlib.util, os
SK = '/root/.claude/skills/synced/60ce1664-4d17-460d-b302-b82a331003e8_e93f8626-2c5f-451f-b2f1-f77923eff6ed/effects'
FD = '/tmp/claude-0/-home-user-try/53a849aa-feae-56a8-8b67-e97274e65d3a/scratchpad/fonts'
spec = importlib.util.spec_from_file_location('fx', SK + '/scripts/fx.py'); fx = importlib.util.module_from_spec(spec); spec.loader.exec_module(fx)
IT = FD + '/InterTight[wght].ttf'; ISI = FD + '/InstrumentSerif-Italic.ttf'; ISR = FD + '/InstrumentSerif-Regular.ttf'
fx.FONT.update({'bold': IT, 'uib': IT, 'uim': IT, 'ui': IT, 'mono': IT, 'didone': ISI, 'serif': ISI})
fx.WGHT.update({'bold': (800,), 'uib': (800,), 'uim': (500,), 'ui': (600,), 'mono': (600,)}); fx.WGHT.pop('didone', None)
