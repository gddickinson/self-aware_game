// node web/static/sim_engine.test.mjs: the JS engine must replay the Python game's seeded runs exactly.
// Fixture: tests/fixtures/sim_fixtures.json, written by scripts/make_sim_fixtures.py from the real desktop code.
import { readFileSync } from 'node:fs';
import assert from 'node:assert/strict';
import { PyRandom } from './py_random.js';
import { Game } from './sim_world.js';
import { replay } from './sim_snapshot.js';
import * as T from './sim_texts.js';

const fx = JSON.parse(readFileSync(new URL('../../tests/fixtures/sim_fixtures.json', import.meta.url)));
let checks = 0;

for (const p of fx.prng) {
  const r = new PyRandom(p.seed);
  assert.deepEqual([0, 1, 2, 3, 4].map(() => r.random()), p.random, `random() seed ${p.seed}`);
  assert.deepEqual([0, 1, 2, 3, 4].map(() => r.randint(-100, 1200)), p.randint, `randint seed ${p.seed}`);
  for (const u of p.uniform) assert.ok(Math.abs(r.uniform(3, 8) - u) < 1e-12, `uniform seed ${p.seed}`);
  checks += 13;
}

const T_MAP = { character: T.CHARACTER_THOUGHTS, observations: T.SNAKE_GAME_OBSERVATIONS,
  fourthWall: T.FOURTH_WALL_THOUGHTS, snake: T.SNAKE_THOUGHTS, controls: T.CONTROLS_HELP };
for (const [k, v] of Object.entries(T_MAP)) { assert.deepEqual(v, fx.texts[k], `text list ${k}`); checks += 1; }

let frames = 0;
for (const c of fx.cases) {
  const { checked, first } = replay(Game, c);
  assert.equal(first, null, `${c.name} (seed ${c.seed}): ${first}`);
  assert.equal(checked, c.snaps.length);
  checks += checked; frames += c.frames;
  console.log(`ok  ${c.name}: seed ${c.seed}, ${c.frames} frames, ${checked} snapshots match`);
}
console.log(`sim engine: ${fx.cases.length} Python runs (${frames} frames), ${checks} checks, all identical`);
