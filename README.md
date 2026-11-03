# bridge-short-render

Render pipeline for a 67.5 s vertical (portrait) cartoon short, "Jembatan yang Ambruk karena Lagu"
(the Broughton Suspension Bridge story, 1831), narrated in Bahasa Indonesia.

Built with the **cartoon-3d-short** skill (from [claude-animated-shorts](https://github.com/mromidev/claude-animated-shorts), MIT):
2D bean-head cartoon characters in a colourful painted 3D world, rendered with three.js inside Remotion.
The GitHub Actions workflow renders all 2,025 frames across 12 parallel jobs, synthesizes the
Indonesian voice-over and the march/SFX soundtrack, assembles the final video, and publishes it as a release asset.
