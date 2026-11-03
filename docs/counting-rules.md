# Counting rules

Four rules keep a Sales Navigator TAM from counting the same company twice.

1. **Count accounts, not people.** Revenue comes from companies. A people search returns every matching person, so one company with three sales leaders counts three times. In our test, 10 software companies held 21 sales leaders. Use the people count only for outreach capacity.
2. **Split by bands that do not overlap.** Company headcount bands (11-50, 51-200, 201-500) are exclusive, so their counts add up. Two searches that share companies (a keyword search and an industry search, or "France" and "Europe") never add up.
3. **Nest each level inside the one above.** SAM is the TAM search plus a region filter. SOM is the SAM search plus one more filter. `scripts/tam.py check` warns when a lower level is bigger than the one above.
4. **Read the right location.** On an account search, the region is the company's headquarters. On a people search, it is where the person lives. In our test, a people search on the US, UK, France and Germany returned a UK-based sales director at a company headquartered in Oslo and a Dallas-based leader at one headquartered in Auckland.

Sales Navigator rounds big counts down (`73K+`). Treat them as floors and say so.

Back to the [README](../README.md).
