# Saans: voice-over script (2:58)

Generated from `docs/video/scenes.mjs`; do not edit by hand. Video: `video/saans-demo.mp4` (rebuild: `node docs/video/make_video.mjs`).

**How to read it:** about 110 words a minute, calm and clear. Start each line when its scene starts; every line fits with a second or two to spare.
Numbers are written the way you say them. Say "Saans" as *sahns* (Hindi साँस, "breath").

### 1. 0:00 – 0:12 · title 

> It is a winter morning in Delhi. The air is at its worst. And at eight forty, Class Seven B goes out for P.E.

### 2. 0:12 – 0:29 · problem 

> Children breathe more air for their size than adults. But on bad-air days, schools get two options. A normal day, or school closed. Nothing tells the principal what to do with period two.

### 3. 0:29 – 0:44 · Delhi, 19 Nov 2025 

> This is Saans. Here is a real bad day, recorded in Delhi on the nineteenth of November, twenty twenty-five. Air quality: three hundred fifty-one. Very Poor. Two changes needed today.

### 4. 0:44 – 1:10 · Same day, different hour: AQI 351 → 127 

> Saans reads the hourly forecast for the school. It applies India’s A.Q.I., and a clear school protocol. Assembly moves indoors. And for P.E., Saans finds a cleaner hour. Swap with Period Eight, at one forty. The A.Q.I. drops from three fifty-one to one twenty-seven. Students with asthma get their own, stricter advice.

### 5. 1:10 – 1:24 · 40 students out of Very Poor air 

> Saans also estimates the benefit. This swap would move forty students out of Very Poor air, with about sixty percent less P.M. two point five. And it shows the formula.

### 6. 1:24 – 1:33 · Every number shows its source 

> Indoor classes stay as they are. And every screen says where its numbers come from.

### 7. 1:33 – 1:52 · Parent notice · English / हिंदी 

> One tap gives parents a notice. In English, or in Hindi. It offers the swap. It does not pretend it is decided. Then share it on WhatsApp.

### 8. 1:52 – 2:20 · Every number checked against the plan 

> Ask Saans is an A.I. agent, built with Strands Agents. It answers from the same plan, using tools. And then we check its work. Every number in the answer must match the plan. If it does not, Saans shows the plan itself.

### 9. 2:20 – 2:34 · Calibrated only with fresh monitor data 

> On a live day, Saans calibrates against government monitors, only when their reading is fresh. If not, it says so. The week view plans ahead.

### 10. 2:34 – 2:52 · aws 

> It runs on A.W.S. Lambda and A.P.I. Gateway for the A.P.I. DynamoDB for schools and daily plans. EventBridge Scheduler runs it at six A.M., India time. CloudWatch and S.N.S. alert us. Amplify hosts the app. All deployed with A.W.S. SAM.

### 11. 2:52 – 2:58 · end 

> Saans. Cleaner hours for every child. Team Chernobyl.

## Recording the voice-over

1. **Read along with the prompter:** play `video/saans-demo-prompter.mp4`. It shows the line to read now, the next line, and a yellow bar for the time left in each scene. Record your voice while it plays, with headphones on so the mic doesn't pick up the video.
   - **iMovie:** import `saans-demo-prompter.mp4` → Window → Record Voiceover → record over the whole timeline. Then select the voice clip → File → Share → File… (audio only), or drag the voice clip onto `saans-demo.mp4` in a new project and export.
   - **Or** record with QuickTime (File → New Audio Recording) while the prompter plays in another window, starting both at the same moment.
2. **Put your voice on the clean video** (if you recorded a separate audio file, e.g. `voice.m4a`):

```bash
ffmpeg -i video/saans-demo.mp4 -i voice.m4a -map 0:v -map 1:a -c:v copy -c:a aac -b:a 192k -shortest video/saans-final.mp4
```

   If your voice starts late or early, add `-itsoffset -0.5` (or `0.5`) before `-i voice.m4a` to shift it.
3. Submit `saans-final.mp4` (not the prompter copy).
