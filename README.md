# CapsGAT

<img width="100" height="100" alt="logo" src="https://github.com/user-attachments/assets/c1cfd5d3-614c-4769-8ffd-87673cd6e5a2" />

CapsGAT is a tool for reformatting subtitle files (.SRT, .JSON, .TSV, .TXT) into interview transcripts. CapsGAT simplifies assigning speakers to segments quickly using keyboard shortcuts.

<img width="1606" height="1006" alt="capsgat_screenshot" src="https://github.com/user-attachments/assets/9efaa0fa-7158-4ddf-8092-fe76e80901af" />



Audio files can be imported and synced to the transcript. This is meant to reduce window-switching and simplify the formatting process. CapsGAT features basic GAT2-editing functionality such as segment splitting and merging, overlapping speech, pauses and comments. 

However, it is not meant as a replacement for professional transcription software (for full-fledged, professional transcription software, check out EXMARaLDA: www.exmaralda.org; importing subtitle files seems to be implemented in newer versions as well), but more as a complementary tool to be used with transcription AI models such as Whisper AI or CapsWriter.

CapsGAT projects can be loaded or saved. Transcripts can be exported as .HTML or .TXT files. With the exception of segments containing unassigned pauses, only segments that have been assigned are included in the transcripts that are exported. The format for interview transcripts is based on the minimal GAT2 transcription convention, though many aspects (such as multiple tiers) are not implemented.

CapsGAT was developed using AI.
