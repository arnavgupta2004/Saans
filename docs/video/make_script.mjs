// Writes docs/video/SCRIPT.md from scenes.mjs.  Usage: node docs/video/make_script.mjs
import { writeFileSync } from 'node:fs';
import { SCENES, starts, mmss } from './scenes.mjs';
const at = starts();
const total = at.at(-1) + SCENES.at(-1).dur;
const words = SCENES.reduce((n, s) => n + s.vo.split(/\s+/).length, 0);
let md = `# Saans: voice-over script (${mmss(total)})

Generated from \`docs/video/scenes.mjs\`; do not edit by hand. Video: \`video/saans-demo.mp4\` (rebuild: \`node docs/video/make_video.mjs\`).

**How to read it:** about ${Math.round(words / (total / 60))} words a minute, calm and clear. Start each line when its scene starts; every line fits with a second or two to spare.
Numbers are written the way you say them. Say "Saans" as *sahns* (Hindi साँस, "breath").

`;
SCENES.forEach((s, i) => {
  md += `### ${i + 1}. ${mmss(at[i])} – ${mmss(at[i] + s.dur)} · ${s.caption || s.id} \n\n> ${s.vo}\n\n`;
});
md += `## Recording the voice-over

1. **Read along with the prompter:** play \`video/saans-demo-prompter.mp4\`. It shows the line to read now, the next line, and a yellow bar for the time left in each scene. Record your voice while it plays, with headphones on so the mic doesn't pick up the video.
   - **iMovie:** import \`saans-demo-prompter.mp4\` → Window → Record Voiceover → record over the whole timeline. Then select the voice clip → File → Share → File… (audio only), or drag the voice clip onto \`saans-demo.mp4\` in a new project and export.
   - **Or** record with QuickTime (File → New Audio Recording) while the prompter plays in another window, starting both at the same moment.
2. **Put your voice on the clean video** (if you recorded a separate audio file, e.g. \`voice.m4a\`):

\`\`\`bash
ffmpeg -i video/saans-demo.mp4 -i voice.m4a -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest video/saans-final.mp4
\`\`\`

   If your voice starts late or early, add \`-itsoffset -0.5\` (or \`0.5\`) before \`-i voice.m4a\` to shift it.
3. Submit \`saans-final.mp4\` (not the prompter copy).
`;
writeFileSync(new URL('./SCRIPT.md', import.meta.url), md);
console.log(`SCRIPT.md: ${SCENES.length} scenes, ${words} words, ${mmss(total)}`);
