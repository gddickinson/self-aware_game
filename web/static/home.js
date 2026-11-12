// Home page: hero with a frame of seed 0 drawn by the browser engine, counts from /api/info, cards, how it works.
import { route, api, app, isStatic, $ } from './core.js';
import { Game } from './sim_world.js';
import { draw } from './sim_render.js';

const HERO_FRAME = 3570;  // seed 0: the snake is in Matrix mode, about to transcend

route('home', async () => {
  const info = await api('/info');
  app().innerHTML = `
  <section class="hero split">
    <div>
      <p class="kicker">A game within a game</p>
      <h1 class="glow">Self-Aware Game</h1>
      <p class="lead">A Python simulation featuring self-aware game characters who realize they're in a game. Alex roams
      the world wondering who is watching; inside one building a snake plays Snake, grows more aware with every meal,
      spots a glitch, and breaks out into Alex's world. Here the same game runs in your browser.</p>
      <a class="btn" href="#/world">Open the world</a><a class="btn alt" href="#/thoughts">Read their thoughts</a>
    </div>
    <figure class="hero-view"><canvas id="hero" width="1200" height="800" role="img"
      aria-label="The game world at frame ${HERO_FRAME} of seed 0: the snake game in Matrix mode, Alex outside it"></canvas>
      <figcaption>Seed 0, frame ${HERO_FRAME}: the snake has eaten the glitch and is about to transcend.</figcaption></figure>
  </section>
  <div class="tiles">
    <div class="tile"><b>${info.character_thoughts}</b><span>thoughts Alex can have</span></div>
    <div class="tile"><b>${info.snake_thoughts}</b><span>snake thoughts, one per awareness level</span></div>
    <div class="tile"><b>${info.states.length}</b><span>character states</span></div>
    <div class="tile"><b>${info.keys.length}</b><span>keys the game answers to</span></div>
  </div>
  <div class="grid">
    <a class="card" href="#/world"><b>World</b><small>the simulation, live</small><span>Play, pause, step, change speed and seed, press the
      desktop keys, and inspect Alex, the snake and anything that escapes.</span></a>
    <a class="card" href="#/thoughts"><b>Thoughts</b><small>everything they can say</small><span>Alex's existential, meta and fourth-wall
      thoughts and the snake's awareness ladder, straight from the Python.</span></a>
    <a class="card" href="#/verify"><b>Verify</b><small>browser vs Python</small><span>Replay a run recorded from the Python game and check
      the browser engine matches it frame for frame.</span></a>
    <a class="card" href="#/about"><b>About</b><small>desktop app, web app, credits</small><span>How to run the pygame version and this site locally.</span></a>
  </div>
  <h2>How this site works</h2>
  <div class="flow">
    <div>The game's logic (<code>main.py</code>, <code>modules/character.py</code>, <code>snake_game.py</code>,
      <code>snake_ai.py</code>, <code>entities.py</code>, <code>world.py</code>) is ported line for line to JavaScript,
      including Python's Mersenne Twister, so <code>python main.py --seed N</code> and this page play the same run.</div>
    <div>A node test replays five seeded Python runs (34,400 frames, with every key the game handles) and requires the same
      positions, states, thoughts, snake, Matrix rain and dialogue.</div>
    <div>${isStatic() ? 'Run the app locally (see About) to' : 'Here, in the local app, you can'} send the run you are
      watching, key presses included, to the Python game with "Check with Python".</div>
  </div>`;
  const g = new Game(0);
  for (let i = 0; i < HERO_FRAME; i++) g.step();
  const ctx = $('#hero').getContext('2d');
  draw(ctx, g);
  setTimeout(() => { if ($('#hero')) draw(ctx, g); }, 300);  // again once the sprite sheet has loaded
});
