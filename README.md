# CapsGAT

<img width="150" height="150" alt="logo" src="https://github.com/user-attachments/assets/c1cfd5d3-614c-4769-8ffd-87673cd6e5a2" />

CapsGAT is a simple tool for interviewers to convert subtitle files (.SRT, .JSON, .TSV, .TXT) to interview transcripts by assigning speakers to segments quickly using keyboard shortcuts.

<img width="1222" height="827" alt="preview1" src="https://github.com/user-attachments/assets/7e9a1ea1-fa0a-40fe-bd8a-a145b62f52c8" />

CapsGAT features basic GAT2-editing functionality such as segment splitting and merging, overlapping speech, pauses and comments.

However, it is not meant as a replacement for professional transcription software, but more as a complementary lightweight tool to be used with transcription AI models such as Whisper AI or CapsWriter (for professional, full-fletched transcription software, check out EXMARaLDA: www.exmaralda.org; importing subtitle files seems to be implemented in newer versions as well).

CapsGAT projects can be loaded or saved. Transcripts can be exported as .HTML or .TXT files, with or without time stamps. With the exception of segments containing unassigned pauses, only segments that have been assigned are included in the transcripts that are exported. The format for interview transcripts is based on the minimal GAT2 transcription convention, though many aspects (such as multiple tiers) are not implemented.

CapsGAT was developed using AI.
