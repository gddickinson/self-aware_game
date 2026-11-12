// Entry point: lazy page modules, footer mode text, background rain, router.
import { start, lazy, route, app, isStatic, $ } from './core.js';
import { rain } from './bg.js';

const PAGES = { 'home.js': ['home'], 'world.js': ['world'], 'thoughts.js': ['thoughts'], 'verify.js': ['verify'], 'about.js': ['about'] };
lazy(Object.fromEntries(Object.entries(PAGES).flatMap(([file, names]) => names.map(n => [n, () => import('./' + file)]))));

route('notfound', () => { app().innerHTML = '<h1>Not found</h1><p><a href="#/">Back to the start</a></p>'; });

$('#mode').textContent = isStatic()
  ? 'static site: the game runs in your browser'
  : 'local app: browser engine + Python game at /api';
rain($('#bg'));
start();
