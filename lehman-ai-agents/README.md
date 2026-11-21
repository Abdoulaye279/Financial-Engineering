# Lehman Brothers, July 2008

Lehman filed its last 10-Q on 10 July 2008, two months before going bankrupt. Could an LLM reading it point at the problems? I asked Gemini for the warning signs, each one backed by an exact quote from the filing, and tried two ways of feeding it the document:

- `part1_full_context`: the whole 10-Q in one prompt (535k characters, 110k tokens)
- `part2_rag`: the 10-Q cut into 77 chunks in a Qdrant vector database, only the 10 closest chunks sent (~15k tokens)

Both find the obvious things: the $2.8bn quarterly loss, the $4bn of write-downs, collateral calls, negative capital markets revenues. The full filing gives more (10 signs against 7, including the June share issue and $37.9bn of Level 3 assets that RAG missed).

The part I found most interesting is the quotes. I check every one of them against the source text: 7/10 are exact with the full filing, only 2/7 with RAG. I then went through the failed ones by hand in the PDF. None of the numbers were invented, but the model happily turns a table row into a "quote" ("Leverage ratio 24.34 May 31, 2008"), cuts sentences with "...", or rewrites a date. So asking for exact quotes is not enough, you have to check them.

You need a Gemini API key (free tier works, the RAG indexing waits ~4 min because of the rate limit) and an email in `set_identity` for the SEC.
