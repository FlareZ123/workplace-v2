"""Historical source-header-only K08 ranking: zero heldout semantic paraphrase."""
import k08_blind_author_rank_quote_clean as safe

rank = safe.ranker
rank.ROLE.update({
    2: "First draft for the crew board.",
    6: "Second desk draft.",
    17: "Standby envelope label.",
    18: "Commissioning envelope label.",
})

if __name__ == "__main__":
    rank.main()
