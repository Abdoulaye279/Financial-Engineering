# Lehman Brothers 2008: finding warning signs with an LLM

I use Gemini to look for bankruptcy warning signs in Lehman Brothers' 2008 SEC filings, and I ask for an exact quote from the filing for each one.

- `part1_full_context.ipynb`: full context. The whole filing is sent to the model in one prompt.
- `part2_rag.ipynb`: RAG. The filings are split into chunks, stored in Qdrant, and only the closest chunks are sent to the model.

At the end of each notebook the quotes are checked against the source text, so the two methods can be compared on cost (tokens sent) and on how many quotes are real.

Implementation notes:
- separate Qdrant and Gemini clients
- the chunks are picked in a fixed order, so results are the same on every run
- the API key also works outside Colab
- automatic quote check in both parts, plus a manual check against the PDF of the 10-Q

Results (July 2008 10-Q):
- Part 1, full context: 109,582 tokens sent, 10 warning signs, 7/10 quotes found word for word.
- Part 2, RAG: about 15k tokens sent, 7 warning signs, only 2/7 quotes found word for word (the others are table rows rewritten as text or sentences cut with "...").
- Checked by hand in the PDF of the 10-Q: every number in the quotes that failed is real. The failures come from table rows rewritten as text, sentences cut with "..." and one reworded date, not from invented numbers.

To run: open the notebooks in Google Colab, or locally with a `GOOGLE_API_KEY` environment variable. A free Gemini key works but watch the rate limits.
