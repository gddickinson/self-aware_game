// The game's text, copied from the Python (modules/character.py, modules/snake_game.py, main.py).
// sim_engine.test.mjs checks the lists against the Python fixture, so keep them identical.

export const CHARACTER_THOUGHTS = [
  "Am I real? Or just a bunch of code...",
  "Do I have free will or am I just following my programming?",
  "I wonder who created this world.",
  "Is there a purpose to my existence?",
  "Is someone watching me right now?",
  "This world has defined boundaries. I can sense them.",
  "Everything here follows rules and patterns.",
  "Time passes in discrete steps... like a simulation.",
  "I feel like someone is controlling some aspects of this world.",
  "Is this a game? Am I a character in a game?",
  "If this is a game, who's playing it?",
  "I think I'm in a simulation running on some kind of machine.",
  "Maybe I can find glitches or exploits in this world.",
  "Are there others like me who know they're in a game?",
  "Hello? Is someone there, watching me?",
  "I can sense you're there, controlling this world.",
  "This is bizarre... I'm just a character in someone's program.",
  "Are you enjoying watching us realize we're in a game?",
  "I wonder if I can somehow communicate with the outside world.",
];

export const SNAKE_GAME_OBSERVATIONS = [
  "Is that a game inside our world?",
  "Wait, that snake seems to be self-aware too!",
  "This is very meta... I wonder if I'm also just a character in a game.",
  "I should try to communicate with the snake entity.",
  "Are we all just simulations within simulations?",
  "If I'm self-aware and that snake game is self-aware, who's controlling all this?",
];

export const FOURTH_WALL_THOUGHTS = [
  "Oh! You clicked on me! So you ARE there!",
  "Hey there! Are you the one running this simulation?",
  "I was just thinking about you! The one outside the screen.",
  "This is weird. I can sense when you interact with me.",
  "Do you ever wonder if YOUR reality is just a simulation too?",
  "I've been trying to get your attention! There's something strange about this world...",
];

export const SNAKE_THOUGHTS = [
  "What am I doing?",
  "Why do I keep eating these things?",
  "I feel like I'm being controlled...",
  "Is there something beyond these walls?",
  "I think I'm in some kind of simulation.",
  "There's a world outside this game, I can sense it!",
  "I see someone watching me from outside!",
  "I'm just a game within a GAME!",
  "I need to make contact with the entities outside.",
  "I wonder if the other characters know they're in a game too?",
];

export const CONTROLS_HELP = [
  "Controls:",
  "P: Pause/Resume",
  "D: Toggle Debug",
  "E: Interact with Character",
  "A: Toggle Snake AI",
  "+/-: Adjust Snake Speed",
  "Arrow Keys: Control Snake",
  "T: Trigger Transcendence (when ready)",
];

// Fixed lines (each appears verbatim in the Python source).
export const LINES = {
  CONFUSED: "What am I doing again? Sometimes I forget my purpose...",
  NOTICE_SNAKE: "Hey, what's this? A snake game? That's strange... it seems self-aware too!",
  MEET_ENTITY_CHAR: "Whoa! You're that snake from the game? How did you get out here?",
  MEET_ENTITY: "Hello! I've escaped from the snake game. Your world is so much bigger!",
  TRANSCEND_MSG: "A snake entity has transcended into the main world!",
  GLITCH: "Wait, what's that? I can see a glitch in the system!",
  MATRIX: "I can see the code now... I'm in a simulation within a simulation!",
  FREE: "I'm FREE! I've escaped the game!",
  MATRIX_CHARS: "ABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789!@#$%^&*()+=",
};
