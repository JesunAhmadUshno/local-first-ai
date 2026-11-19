# C1 corpus: source and licence

Recorded 2026-11-17, under decision 0005.

- Work: Ralph Waldo Emerson, essays. The eleven documents are
  The American Scholar, Compensation, Self-Reliance, Friendship,
  Heroism, Manners, Gifts, Nature, Shakespeare; or, The Poet,
  Prudence, and Circles. These are Emerson's own essays, drawn
  from Essays: First Series (1841), Essays: Second Series
  (1844), and the 1837 address The American Scholar.
- Edition fetched: Project Gutenberg eBook #16643, "Essays by
  Ralph Waldo Emerson", Merrill's English Texts edition, edited
  by Edna Henry Lee Turpin (release date September 4, 2005;
  most recently updated April 29, 2022). Fetched 2026-11-17
  from the Project Gutenberg mirror at gutenberg.pglaf.org
  (https://gutenberg.pglaf.org/cache/epub/16643/pg16643.txt),
  567,493 bytes. Raw file kept at raw/ in this folder.
- Licence: the underlying essays are public domain (author died
  1882). Project Gutenberg's own terms state the eBook "is for
  the use of anyone anywhere in the United States and most other
  parts of the world at no cost and with almost no restrictions
  whatsoever" under the Project Gutenberg License. The corpus
  files here contain Emerson's essay text only.
- Excluded from the corpus: the editor's introduction (Life of
  Emerson, Critical Opinions, Chronological List), the
  Publishers' Note, the contents pages, and the entire back
  NOTES section (the editor's footnotes). None of the editor's
  text is in any corpus document.
- Stripped during the split: the editor's bracketed note
  markers ([93], [145] and the like, 602 lines carried them)
  inside the essay text. No words of Emerson's were added,
  removed, or reordered; each document is one essay, in order,
  with CRLF line endings normalised and whitespace collapsed
  within paragraphs.
- Ingest shape: one .txt file per essay, C01 to C11, first line
  "Title: <essay title>", in the repo's own ingest format
  (src/assistant.py ingest_directory, unmodified).
- Measured with the repo's core, 2026-11-17: 11 documents,
  67,633 words, 3,364 sentences, 3,387 chunks (30-word chunks,
  10-word overlap). Corpus fingerprint (repo's own
  corpus_fingerprint, sha256 over per-document hashes):
  7ce2deb4397a61694350425c11a25bd64c4fd4092a32e35d7df76e287822183b
- Per document: C01 The American Scholar 7,826 words; C02
  Compensation 7,728; C03 Self-Reliance 10,120; C04 Friendship
  5,936; C05 Heroism 4,268; C06 Manners 8,065; C07 Gifts 1,531;
  C08 Nature 6,242; C09 Shakespeare; or, The Poet 6,600; C10
  Prudence 4,539; C11 Circles 4,778.
